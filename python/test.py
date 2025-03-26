import numpy as np
import matplotlib.pyplot as plt
from main import CircleFitter

class CircleFitterTest:
    def __init__(self, image_path, weight_matrix_path, initial_x, initial_y, search_area, min_radius, max_radius, pixel_size_nm):
        """
        Initializes the test for comparing intensity computation methods.

        Parameters:
        - image_path (str): Path to the image sequence.
        - weight_matrix_path (str): Path to the weight matrices file.
        - initial_x, initial_y (int): Initial center guess.
        - search_area (int): Search area for center.
        - min_radius, max_radius (int): Allowed radius range.
        - pixel_size_nm (float): Pixel size in nanometers.
        """
        self.image_path = image_path
        self.weight_matrix_path = weight_matrix_path
        self.initial_x = initial_x
        self.initial_y = initial_y
        self.search_area = search_area
        self.min_radius = min_radius
        self.max_radius = max_radius
        self.pixel_size_nm = pixel_size_nm

        self.standard_intensities = []
        self.weight_matrix_intensities = []

    def run_test(self):
        """ Runs the circle fitting with both methods and compares results. """
        fitter_standard = CircleFitter(
            self.image_path, None, self.initial_x, self.initial_y,
            self.search_area, self.min_radius, self.max_radius, self.pixel_size_nm, method="standard"
        )
        fitter_weight_matrix = CircleFitter(
            self.image_path, self.weight_matrix_path, self.initial_x, self.initial_y,
            self.search_area, self.min_radius, self.max_radius, self.pixel_size_nm, method="weight_matrix"
        )

        for frame_index in range(fitter_standard.num_frames):
            print(f"Processing frame {frame_index + 1}/{fitter_standard.num_frames}...")

            frame_standard = fitter_standard.preprocess_frame(fitter_standard.image_stack[frame_index].astype(float))
            frame_weight_matrix = fitter_weight_matrix.preprocess_frame(fitter_weight_matrix.image_stack[frame_index].astype(float))

            # Get best circle parameters using standard method
            x_s, y_s, r_s = fitter_standard.find_best_circle(frame_standard, self.min_radius, self.max_radius, self.search_area)

            # Compute intensity using both methods for the same (x, y, r)
            intensity_standard = fitter_standard.compute_intensity(frame_standard, x_s, y_s, r_s)
            intensity_weight_matrix = fitter_weight_matrix.compute_intensity(frame_weight_matrix, x_s, y_s, r_s)

            self.standard_intensities.append(intensity_standard)
            self.weight_matrix_intensities.append(intensity_weight_matrix)

        self.compare_results()

    def compare_results(self):
        """ Compares the intensity values from both methods. """
        standard_arr = np.array(self.standard_intensities)
        weight_matrix_arr = np.array(self.weight_matrix_intensities)

        # Compute difference metrics
        diff = np.abs(standard_arr - weight_matrix_arr)
        mean_diff = np.mean(diff)
        std_diff = np.std(diff)
        correlation = np.corrcoef(standard_arr, weight_matrix_arr)[0, 1]

        print("\n🔍 **Comparison Results:**")
        print(f"📊 Mean Absolute Difference: {mean_diff:.4f}")
        print(f"📈 Standard Deviation of Differences: {std_diff:.4f}")
        print(f"🔗 Correlation: {correlation:.4f}")

        # Plot intensity values
        plt.figure(figsize=(10, 5))
        plt.plot(standard_arr, label="Standard Method", marker="o")
        plt.plot(weight_matrix_arr, label="Weight Matrix Method", marker="x")
        plt.xlabel("Frame")
        plt.ylabel("Intensity")
        plt.legend()
        plt.title("Comparison of Intensity Computation Methods")
        plt.show()

        # Plot difference distribution
        plt.figure(figsize=(10, 5))
        plt.hist(diff, bins=20, alpha=0.7, color="blue")
        plt.xlabel("Absolute Difference")
        plt.ylabel("Frequency")
        plt.title("Distribution of Differences Between Methods")
        plt.show()


# Run the test
if __name__ == "__main__":
    test = CircleFitterTest(
        image_path="python/my_example.tif",
        weight_matrix_path="weight_matrices.npz",
        initial_x=50,
        initial_y=47,
        search_area=5,
        min_radius=4,
        max_radius=7,
        pixel_size_nm=65
    )
    test.run_test()
