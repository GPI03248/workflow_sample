# API: cfd.io_output

Result output utilities.

Responsibilities:
    - Save solver results to CSV, NPZ, PNG, and Markdown.
    - Handle missing matplotlib gracefully.

Does NOT:
    - Perform any computation.

## Functions

### `save_results(output_dir, U, mesh, n_steps, actual_final_time, gamma, case_name, centerline_x)`
Save CFD results to disk.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
