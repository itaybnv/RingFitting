from main import CircleFitter

my_example_image_path = "python/my_example.tif"
example_image_path = "python/example.tif"
test_weight_matrix_path = "weight_matrices.npz"

my_example_parameters = {"image_path": my_example_image_path, 
                            "weight_matrix_path": test_weight_matrix_path, 
                            "initial_x": 50, "initial_y": 47,
                            "search_area": 5, 
                            "min_radius": 5, "max_radius": 6, 
                            "pixel_size_nm": 65}

example_parameters = {"image_path": example_image_path, 
                        "weight_matrix_path": test_weight_matrix_path, 
                        "initial_x": 65, "initial_y": 59,
                        "search_area": 5, 
                        "min_radius": 7, "max_radius": 11, 
                        "pixel_size_nm": 65}

print("Running CircleFitter in standard mode...")
fitter_standard = CircleFitter(**example_parameters, method="standard")
# fitter_standard.fit_frame(0)
fitter_standard.process_all_frames()

# print("\nRunning CircleFitter in weight matrix mode...")
# fitter_weight_matrix = CircleFitter(**example_parameters, method="weight_matrix")
# # fitter_weight_matrix.fit_frame(0)
# fitter_weight_matrix.process_all_frames()
print("\n✅ Test case completed.")
