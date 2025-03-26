import numpy as np
import tifffile
import matplotlib.pyplot as plt

class RingImageGenerator:
    def __init__(self, output_path, num_frames=10, image_size=(100, 100),
                 radius_range=(10, 20), center_range=((45, 55), (45, 55)),
                 ring_thickness=3, ring_imperfection=0.0, ring_lopsidedness=0.0,
                 background_noise=0.0, edge_fade=0.0):
        """
        Generates synthetic multi-frame TIFF images containing rings for testing CircleFitter.

        Parameters:
        - output_path (str): File path to save the generated TIFF.
        - num_frames (int): Number of frames in the TIFF sequence.
        - image_size (tuple): Size of the images (height, width).
        - radius_range (tuple): Min and max radius values for rings.
        - center_range (tuple of tuples): Allowed x and y range for circle centers.
        - ring_thickness (int): Thickness of the ring in pixels.
        - ring_imperfection (float): 0.0 = perfect ring, 1.0 = strong noise.
        - ring_lopsidedness (float): 0.0 = no brightness variation, 1.0 = strong lopsided effect.
        - background_noise (float): 0.0 = no noise, 1.0 = strong noise.
        - edge_fade (float): 0.0 = no fade, 1.0 = full fade at inner and outer edges.
        """
        self.output_path = output_path
        self.num_frames = num_frames
        self.image_size = image_size
        self.radius_range = radius_range
        self.center_range = center_range
        self.ring_thickness = ring_thickness
        self.ring_imperfection = ring_imperfection
        self.ring_lopsidedness = ring_lopsidedness
        self.background_noise = background_noise
        self.edge_fade = edge_fade

    def generate_frame(self, radius, center_x, center_y):
        """Generates a single frame with a ring at the specified parameters."""
        height, width = self.image_size
        y_indices, x_indices = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')
        
        # Compute distance from each pixel center to the ring center
        distances = np.sqrt((x_indices - center_x) ** 2 + (y_indices - center_y) ** 2)
        
        # Create a binary mask for the ring
        ring_mask = (radius - self.ring_thickness / 2 <= distances) & (distances <= radius + self.ring_thickness / 2)
        
        # Apply ring_imperfection (adds noise if greater than 0.0)
        if self.ring_imperfection > 0.0:
            noise = np.random.uniform(-self.ring_thickness / 2, self.ring_thickness / 2, size=distances.shape)
            noise *= self.ring_imperfection  # Scale noise by imperfection level
            ring_mask &= (radius + noise - self.ring_thickness / 2 <= distances) & (distances <= radius + noise + self.ring_thickness / 2)
        
        # Apply ring_lopsidedness (one side brighter, one side dimmer)
        brightness = np.ones_like(distances) * ring_mask
        if self.ring_lopsidedness > 0.0:
            angle = np.random.uniform(0, 2 * np.pi)  # Random lopsided effect angle
            lopsided_mask = np.cos(angle) * (x_indices - center_x) + np.sin(angle) * (y_indices - center_y)
            lopsided_mask = (lopsided_mask > 0).astype(float)  # One side bright, one side dim
            brightness *= (1 - self.ring_lopsidedness * (1 - lopsided_mask))
        
        # Apply edge fading effect
        if self.edge_fade > 0.0:
            fade_inner = (distances - (radius - self.ring_thickness / 2)) / (self.ring_thickness / 2)
            fade_outer = ((radius + self.ring_thickness / 2) - distances) / (self.ring_thickness / 2)
            fade_mask = np.clip(np.minimum(fade_inner, fade_outer), 0, 1)
            brightness *= fade_mask ** self.edge_fade  # Corrected scaling so edge_fade=1 means full fade
        
        # Apply background noise
        if self.background_noise > 0.0:
            noise_layer = np.random.uniform(0, self.background_noise * 65535, size=brightness.shape)
            brightness = np.clip(brightness * 65535 + noise_layer, 0, 65535)
        else:
            brightness *= 65535
        
        return brightness.astype(np.uint16)

    def generate_sequence(self):
        """Generates and saves a multi-frame TIFF file in 16-bit grayscale."""
        frames = []
        for _ in range(self.num_frames):
            radius = np.random.uniform(*self.radius_range)
            center_x = np.random.uniform(*self.center_range[0])
            center_y = np.random.uniform(*self.center_range[1])
            frame = self.generate_frame(radius, center_x, center_y)
            frames.append(frame)
        
        tifffile.imwrite(self.output_path, np.array(frames), dtype=np.uint16, imagej=True)
        print(f"Saved synthetic ring dataset to {self.output_path}")

if __name__ == "__main__":
    generator = RingImageGenerator(
        output_path="synthetic_rings.tif",
        num_frames=10,
        radius_range=(10, 12),
        center_range=((48, 52), (48, 52)),
        ring_thickness=4,
        ring_imperfection=1,
        ring_lopsidedness=0.4,
        background_noise=1,
        edge_fade=1
    )
    generator.generate_sequence()
