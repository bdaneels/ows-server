# Feature Ideas for OWS Server

Based on the analysis of the repository, here are three feature ideas to enhance the application:

## 1. Output File Preview
**Problem:** Users currently have to download the generated output file (Excel or CSV) to verify if the script produced the expected results. This is time-consuming and inefficient.
**Solution:** Implement an in-browser preview of the generated output file.
**Implementation Details:**
- Modify `page_run_script` to detect when an output file is generated.
- Use `pandas` to read the first N rows (e.g., 20) of the output file.
- Display these rows using a NiceGUI `aggrid` component directly on the results page.
- Handle both CSV and Excel formats.

## 2. Execution History and Logs
**Problem:** There is no persistent record of who ran what script and when. Once the user navigates away from the result page, the execution logs (stdout/stderr) are lost.
**Solution:** Create a history system that logs every script execution.
**Implementation Details:**
- Create a `history/` directory to store execution metadata (JSON files).
- Save details such as timestamp, user, script name, input filenames, output filename, and full stdout/stderr logs.
- Add a new page `/history` to the application menu.
- Display a table of past executions, allowing users to drill down into details and view logs.

## 3. Dynamic Script Arguments
**Problem:** Scripts are currently limited to receiving exactly two input files. Many scripts might require additional parameters (e.g., thresholds, specific modes, date ranges) which are currently impossible to pass via the UI without creating multiple versions of the same script.
**Solution:** specific arguments configuration in `ows.ini`.
**Implementation Details:**
- Allow defining arguments in `ows.ini` for each script (e.g., `[args_scriptname]`).
- Supported types could include string, integer, float, boolean (checkbox).
- Dynamically render these inputs in the `Select Script` or `Upload Files` page.
- Pass these arguments to the underlying Python script via command-line flags (e.g., `--threshold 0.5`).
