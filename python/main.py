import numpy as np
import tifffile
import matplotlib.pyplot as plt
from scipy.interpolate import RectBivariateSpline

class CircleFitter:
    def __init__(self, image_path, weight_matrix_path=None, initial_x=66, initial_y=59,
                 search_area=5, min_radius=7, max_radius=12, pixel_size_nm=65, method="standard"):
        """ Initializes the CircleFitter with image and fitting parameters. """
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
        self.initial_x, self.initial_y = global_x, global_y

        # 10x Precision Fit (With 2D Interpolation)
        refined_x, refined_y, refined_radius = self.refine_circle_fit(processed_frame, global_x, global_y, estimated_radius, crop_bounds)

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

    def refine_circle_fit(self, image, center_x, center_y, estimated_radius, crop_bounds):
        """ Refines the circle fit at 10x precision using interpolation. """
        interpolation_factor = 10

        # Define cropped region in the original image
        y_range = np.arange(crop_bounds[0], crop_bounds[1])
        x_range = np.arange(crop_bounds[2], crop_bounds[3])
        cropped_image = image[crop_bounds[0]:crop_bounds[1], crop_bounds[2]:crop_bounds[3]]

        # 2D Interpolation to create a finer resolution grid
        interp_func = RectBivariateSpline(y_range, x_range, cropped_image)

        # Create high-resolution grid (10x finer)
        new_y = np.linspace(y_range[0], y_range[-1], len(y_range) * interpolation_factor)
        new_x = np.linspace(x_range[0], x_range[-1], len(x_range) * interpolation_factor)
        interpolated_image = interp_func(new_y, new_x)

        # Convert 1x precision results to 10x scale
        refined_initial_x = (center_x - crop_bounds[2]) * interpolation_factor
        refined_initial_y = (center_y - crop_bounds[0]) * interpolation_factor
        refined_radius = estimated_radius * interpolation_factor

        # Define refined search area (±0.5 pixels in original scale → ±5 in 10x scale)
        search_range = 5  # 10x of ±0.5 pixels

        # Perform a refined search on the full interpolated cropped image
        best_x, best_y, best_radius = self.find_best_circle(
            interpolated_image,
            int(refined_radius - search_range),
            int(refined_radius + search_range),
            search_range,
            initial_x=int(refined_initial_x),
            initial_y=int(refined_initial_y)
        )

        # Convert refined results back to full image scale
        return (
            best_x / interpolation_factor + crop_bounds[2],
            best_y / interpolation_factor + crop_bounds[0],
            best_radius / interpolation_factor
        )

    def find_best_circle(self, cropped_frame, min_radius, max_radius, search_range, initial_x=None, initial_y=None):
        """ Finds the best circle by scanning center (x, y) and radius. """
        height, width = cropped_frame.shape

        # If no initial guess is provided, default to the cropped image center
        if initial_x is None:
            initial_x = width // 2
        if initial_y is None:
            initial_y = height // 2

        best_intensity = -np.inf
        best_params = (initial_x, initial_y, min_radius)

        for radius in range(min_radius, max_radius + 1):
            for dx in range(-search_range, search_range + 1):
                for dy in range(-search_range, search_range + 1):
                    test_x = initial_x + dx
                    test_y = initial_y + dy

                    if 0 <= test_x < width and 0 <= test_y < height:
                        intensity = self.compute_intensity(cropped_frame, test_x, test_y, radius)

                        if intensity > best_intensity:
                            best_intensity = intensity
                            best_params = (test_x, test_y, radius)

        return best_params

    def compute_intensity(self, image, x_center, y_center, radius):
        """ Computes intensity using the selected method: 'standard' or 'weight_matrix'. """
        if self.method == "standard":
            return self.compute_standard_intensity(image, x_center, y_center, radius)
        elif self.method == "weight_matrix":
            return self.compute_weight_matrix_intensity(image, x_center, y_center, radius)

    @staticmethod
    def compute_standard_intensity(image, x_center, y_center, radius):
        """ Computes intensity by averaging pixels whose centers are within 0.5 pixels of the circle perimeter. """
        height, width = image.shape

        # Create coordinate grids for all pixels
        y_indices, x_indices = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')

        # Compute distance of every pixel center to the circle perimeter
        distances = np.abs(np.sqrt((x_indices - x_center) ** 2 + (y_indices - y_center) ** 2) - radius)

        # Get mask of pixels within 0.5 pixels of the perimeter
        mask = distances < 0.5

        # Compute the average intensity of the selected pixels
        return np.mean(image[mask]) if np.any(mask) else 0  # Avoid division by zero


    def compute_weight_matrix_intensity(self, image, x_center, y_center, radius):
        """ Uses weight matrices to compute intensity. """
        weight_matrix = self.weight_matrices[str(radius)]
        weight_size = weight_matrix.shape[0]

        x_start = max(0, min(int(x_center - weight_size // 2), image.shape[1] - weight_size))
        y_start = max(0, min(int(y_center - weight_size // 2), image.shape[0] - weight_size))

        padded_image = np.zeros_like(image)
        padded_image[y_start:y_start + weight_size, x_start:x_start + weight_size] = weight_matrix

        return np.sum(image * padded_image)
    
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

if __name__ == "__main__":
    test_image_path = "gaussian_ring.tif"
    test_weight_matrix_path = "weight_matrices.npz"

    fitter = CircleFitter(test_image_path, initial_x=50, initial_y=50, min_radius=4, max_radius=10 ,method="standard")
    fitter.fit_frame(0)
    
    fitter = CircleFitter(test_image_path, test_weight_matrix_path, initial_x=50, initial_y=50, min_radius=4, max_radius=8, method="weight_matrix")
    fitter.fit_frame(0)

    print("\n✅ Test case completed.")
