import numpy as np
import tifffile
import matplotlib.pyplot as plt
from scipy.interpolate import RectBivariateSpline

class CircleFitter:
    def __init__(self, image_path, weight_matrix_path=None, initial_x=66, initial_y=59,
                 search_area=5, min_radius=7, max_radius=12, pixel_size_nm=65, method="standard"):
        """
        Initializes the CircleFitter with image and fitting parameters.

        Parameters:
        - image_path (str): Path to the image sequence.
        - weight_matrix_path (str, optional): Path to the .npz file containing weight matrices.
        - initial_x, initial_y (int): Initial center guess.
        - search_area (int): Search area for center.
        - min_radius, max_radius (int): Allowed radius range.
        - pixel_size_nm (float): Pixel size in nanometers.
        - method (str): "standard" (default) or "weight_matrix" for intensity computation.
        """
        self.image_path = image_path
        self.weight_matrix_path = weight_matrix_path
        self.initial_x = initial_x
        self.initial_y = initial_y
        self.search_area = search_area
        self.min_radius = min_radius
        self.max_radius = max_radius
        self.pixel_size_nm = pixel_size_nm
        self.method = method  # "standard" or "weight_matrix"

        self.load_image_sequence()
        if self.method == "weight_matrix":
            self.load_weight_matrices()

        self.fitted_radii = []
        self.refined_x_positions = []
        self.refined_y_positions = []

    def load_image_sequence(self):
        """ Loads the TIFF image sequence. """
        self.image_stack = tifffile.imread(self.image_path)
        self.num_frames = self.image_stack.shape[0]

    def load_weight_matrices(self):
        """ Loads the weight matrices from the .npz file (only if method is weight_matrix). """
        if self.weight_matrix_path is None:
            raise ValueError("Weight matrix path must be provided when using method='weight_matrix'.")
        self.weight_matrices = np.load(self.weight_matrix_path)

    def preprocess_frame(self, frame):
        """ Performs background subtraction. """
        background_region = frame[:10, :10]
        background_mean = np.mean(background_region)
        return frame - background_mean

    def fit_frame(self, frame_index):
        """ Processes a single frame and fits the best circle. """
        processed_frame = self.preprocess_frame(self.image_stack[frame_index].astype(float))

        crop_bounds = [self.initial_y - 15, self.initial_y + 15, self.initial_x - 15, self.initial_x + 15]
        cropped_frame = processed_frame[crop_bounds[0]:crop_bounds[1], crop_bounds[2]:crop_bounds[3]]

        # 1x Precision Fit
        center_x, center_y, estimated_radius = self.find_best_circle(cropped_frame, self.min_radius, self.max_radius, self.search_area)

        # Convert to global coordinates
        global_x = center_x + crop_bounds[2]
        global_y = center_y + crop_bounds[0]
        print(global_x, global_y)
        self.initial_x, self.initial_y = global_x, global_y

        # 10x Precision Fit (With 2D Interpolation)
        refined_x, refined_y, refined_radius = self.refine_circle_fit(processed_frame, center_x, center_y, estimated_radius, crop_bounds)

        # Store results
        self.refined_x_positions.append(refined_x)
        self.refined_y_positions.append(refined_y)
        self.fitted_radii.append(refined_radius)

        self.plot_fitted_circle(frame_index, processed_frame, refined_x, refined_y, refined_radius)

    def process_all_frames(self):
        """ Processes all frames in the sequence. """
        for t in range(self.num_frames):
            self.fit_frame(t)
        self.plot_radius_vs_frame()

    def plot_fitted_circle(self, frame_index, frame, x_center, y_center, radius):
        """ Plots the fitted circle on the current frame. """
        plt.figure()
        plt.imshow(frame, cmap="gray")
        plt.gca().add_patch(plt.Circle((x_center, y_center), radius, color="b", fill=False))
        plt.plot(x_center, y_center, "r.", markersize=10)
        plt.title(f"Frame {frame_index+1}: r = {radius:.2f} pixels = {radius * self.pixel_size_nm:.2f} nm")
        plt.show()

    def plot_radius_vs_frame(self):
        """ Plots the radius variation over frames. """
        plt.figure()
        plt.scatter(range(1, self.num_frames + 1), np.array(self.fitted_radii) * self.pixel_size_nm, color="k")
        plt.title("Radius Vs. Frame")
        plt.xlabel("Frame")
        plt.ylabel("Radius (nm)")
        plt.show()

    def find_best_circle(self, cropped_frame, min_radius, max_radius, search_area):
        """ Finds the best circle by scanning center (x, y) and radius. """
        height, width = cropped_frame.shape
        center_x, center_y = width // 2, height // 2  # Approximate center of cropped region

        best_intensity = -np.inf
        best_params = (center_x, center_y, min_radius)

        # Ensure the search is relative to the cropped frame
        for radius in range(min_radius, max_radius + 1):
            for dx in range(-search_area, search_area + 1):  
                for dy in range(-search_area, search_area + 1):
                    test_x = center_x + dx  # Now relative to the cropped image
                    test_y = center_y + dy  

                    # Ensure (x, y) is within the cropped frame
                    if 0 <= test_x < width and 0 <= test_y < height:
                        intensity = self.compute_intensity(cropped_frame, test_x, test_y, radius)

                        if intensity > best_intensity:
                            best_intensity = intensity
                            best_params = (test_x, test_y, radius)

        print("Best circle found (relative to cropped frame):", best_params)
        return best_params

    def refine_circle_fit(self, image, initial_x, initial_y, estimated_radius, crop_bounds):
        """ Refines the circle fit at 10x precision using interpolation. """
        interpolation_factor = 10

        # Define crop region in the original image
        y_range = np.arange(crop_bounds[0], crop_bounds[1])
        x_range = np.arange(crop_bounds[2], crop_bounds[3])
        cropped_image = image[crop_bounds[0]:crop_bounds[1], crop_bounds[2]:crop_bounds[3]]

        # 2D Interpolation to create a finer resolution grid
        interp_func = RectBivariateSpline(y_range, x_range, cropped_image)

        # Create high-resolution grid (10x finer)
        new_y = np.linspace(y_range[0], y_range[-1], (y_range.size * interpolation_factor))
        new_x = np.linspace(x_range[0], x_range[-1], (x_range.size * interpolation_factor))
        interpolated_image = interp_func(new_y, new_x)

        # Convert initial guess to the interpolated coordinate system
        refined_initial_x = (initial_x - crop_bounds[2]) * interpolation_factor
        refined_initial_y = (initial_y - crop_bounds[0]) * interpolation_factor
        refined_estimated_radius = estimated_radius * interpolation_factor

        # Perform a refined search in the interpolated image
        best_x, best_y, best_radius = self.find_best_circle(
            interpolated_image,
            int(refined_estimated_radius - 5),
            int(refined_estimated_radius + 5),
            5
        )

        # Convert refined results back to original scale
        return (
            best_x / interpolation_factor + crop_bounds[2],
            best_y / interpolation_factor + crop_bounds[0],
            best_radius / interpolation_factor
        )


    def compute_intensity(self, image, x_center, y_center, radius):
        """ Computes intensity using the selected method: 'standard' or 'weight_matrix'. """
        if self.method == "standard":
            return self.compute_standard_intensity(image, x_center, y_center, radius)
        elif self.method == "weight_matrix":
            return self.compute_weight_matrix_intensity(image, x_center, y_center, radius)

    @staticmethod
    def compute_standard_intensity(image, x_center, y_center, radius):
        """ Computes intensity along a circular contour using the standard method. """
        theta = np.linspace(0, 2 * np.pi, 360)  # 360 sample points around the circle
        x_points = np.clip((x_center + radius * np.cos(theta)).astype(int), 0, image.shape[1] - 1)
        y_points = np.clip((y_center + radius * np.sin(theta)).astype(int), 0, image.shape[0] - 1)
        
        return np.mean(image[y_points, x_points])

    def compute_weight_matrix_intensity(self, image, x_center, y_center, radius):
        """ Uses weight matrices to compute intensity. """
        weight_matrix = self.weight_matrices[str(radius)]
        weight_size = weight_matrix.shape[0]

        # Ensure placement inside image bounds
        x_start = max(0, min(int(x_center - weight_size // 2), image.shape[1] - weight_size))
        y_start = max(0, min(int(y_center - weight_size // 2), image.shape[0] - weight_size))

        # Create a zero-filled weight image
        padded_image = np.zeros_like(image)
        
        # Insert the weight matrix at the correct position
        padded_image[y_start:y_start + weight_size, x_start:x_start + weight_size] = weight_matrix

        return np.sum(image * padded_image)


if __name__ == "__main__":
    # Small test case
    test_image_path = "python/my_example.tif"
    test_weight_matrix_path = "weight_matrices.npz"

    parameters = {"image_path": test_image_path, 
                  "weight_matrix_path": test_weight_matrix_path, 
                  "initial_x": 50, "initial_y": 47,
                 "search_area": 5, 
                 "min_radius": 2, "max_radius": 10, 
                 "pixel_size_nm": 65}

    print("Running CircleFitter in standard mode...")
    fitter_standard = CircleFitter(**parameters, method="standard")
    fitter_standard.fit_frame(0)

    if test_weight_matrix_path:
        print("\nRunning CircleFitter in weight matrix mode...")
        fitter_weight_matrix = CircleFitter(**parameters, method="weight_matrix")
        fitter_weight_matrix.fit_frame(0)

    print("\n✅ Test case completed.")
