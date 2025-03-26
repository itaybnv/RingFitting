import numpy as np
import tifffile
import matplotlib.pyplot as plt

class GaussianRingGenerator:
    def __init__(self, output_path, num_frames=10, image_size=(100, 100), 
                 radius=20, ring_thickness=5, gaussian_amplitude=50000,
                 gaussian_spread=1.0, noise_level=0.1, baseline_noise_level=0.05):
        """
        Generates synthetic ring images with a Gaussian intensity profile.

        Parameters:
        - output_path (str): Path to save the generated TIFF image sequence.
        - num_frames (int): Number of frames to generate.
        - image_size (tuple): Size of the image (height, width).
        - radius (float): Mean radius of the ring.
        - ring_thickness (float): Standard deviation of the Gaussian peaks.
        - gaussian_amplitude (int): Peak intensity of the Gaussian.
        - gaussian_spread (float): Controls how spread out the Gaussian peaks are.
        - noise_level (float): Scales noise proportional to the square root of pixel intensity.
        - baseline_noise_level (float): Uniform noise level applied to the entire image.
        """
        self.output_path = output_path
        self.num_frames = num_frames
        self.image_size = image_size
        self.radius = radius
        self.ring_thickness = ring_thickness
        self.gaussian_amplitude = gaussian_amplitude
        self.gaussian_spread = gaussian_spread
        self.noise_level = noise_level
        self.baseline_noise_level = baseline_noise_level

    def generate_frame(self):
        """Generates a single frame with a Gaussian-profiled ring."""
        height, width = self.image_size
        y_indices, x_indices = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')

        # Compute distance from each pixel to the image center
        center_x, center_y = width // 2, height // 2
        distances = np.sqrt((x_indices - center_x) ** 2 + (y_indices - center_y) ** 2)

        # Generate Gaussian ring intensity profile
        ring_intensity = self.gaussian_amplitude * np.exp(-((distances - self.radius) ** 2) / 
                                                           (2 * (self.gaussian_spread * self.ring_thickness) ** 2))

        # Add noise proportional to the square root of intensity
        signal_noise = self.noise_level * np.sqrt(np.abs(ring_intensity)) * np.random.randn(*ring_intensity.shape)

        # Add uniform baseline noise
        baseline_noise = self.baseline_noise_level * np.random.randn(*ring_intensity.shape) * self.gaussian_amplitude

        # Combine image with noise
        noisy_image = np.clip(ring_intensity + signal_noise + baseline_noise, 0, 65535).astype(np.uint16)

        return noisy_image

    def save_images(self):
        """Generates and saves a multi-frame 16-bit TIFF image sequence."""
        frames = [self.generate_frame() for _ in range(self.num_frames)]
        tifffile.imwrite(self.output_path, np.array(frames), dtype=np.uint16, imagej=True)
        print(f"Saved synthetic Gaussian ring image sequence to {self.output_path}")

    def plot_sample_frame(self):
        """Plots the first generated frame and its cross-section."""
        image = self.generate_frame()
        
        # Plot the 2D image
        plt.figure(figsize=(6, 6))
        plt.imshow(image, cmap="gray", vmin=0, vmax=65535)
        plt.colorbar(label="Intensity")
        plt.title("Generated Gaussian Ring - First Frame")
        
        # Plot cross-section along the x-axis
        center_y = self.image_size[0] // 2
        x_axis = np.arange(self.image_size[1])
        intensity_profile = image[center_y, :]

        plt.figure(figsize=(6, 4))
        plt.plot(x_axis, intensity_profile, color="b")
        plt.title("Cross-section Intensity Profile (X-Axis)")
        plt.xlabel("X Position")
        plt.ylabel("Intensity")
        plt.grid()

        plt.show()

if __name__ == "__main__":
    generator = GaussianRingGenerator(
        output_path="gaussian_ring.tif",
        num_frames=2,
        image_size=(100, 100),
        radius=7,
        ring_thickness=2,
        gaussian_amplitude=30000,
        gaussian_spread=2,
        noise_level=10,
        baseline_noise_level=0
    )
    generator.save_images()
    generator.plot_sample_frame()
