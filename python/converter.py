import scipy.io
import numpy as np

def convert_mat_to_npz(mat_file_path, npz_file_path):
    """ Converts a MATLAB .mat file containing weight matrices into a compressed .npz file. """
    # Load the MATLAB .mat file
    mat_data = scipy.io.loadmat(mat_file_path)

    # Extract weight matrices (assumes names like 'matrix_1', 'matrix_2', ...)
    weight_matrices = {
        str(int(key.split("_")[1])): mat_data[key]
        for key in mat_data if key.startswith("matrix_")
    }

    # Save as a compressed NumPy .npz file
    np.savez_compressed(npz_file_path, **weight_matrices)
    print(f"✅ Converted and saved to: {npz_file_path}")

mat_file = "matrices.mat"
npz_file = "weight_matrices.npz"

convert_mat_to_npz(mat_file, npz_file)  # Convert .mat to .npz
