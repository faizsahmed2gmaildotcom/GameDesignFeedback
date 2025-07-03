# INSTRUCTIONS
## YOU MUST INSTALL THE "google-genai" PACKAGE FIRST

### 1. Run "gameAnalysis.py"
### 2. Place contextual files in "filesForAnalysis"
   * Files MUST be in PDF/TXT/HTML/CSV/XML format
### 3. Run "gameAnalysis.py". You must choose/create a prompt, file description, and game description.
   * Type "remove" followed by the entry (e.g., "remove Word Nut") to remove that entry
   * Game Descriptions: brief description of the game (e.g., "This is a casual mobile game in which players must sort jumbled characters to form words.")
     * Phrasing depends on the placement of "gameDescription" in the prompt
   * Files Descriptions: file name followed by a brief description on the contents of each file
     * Wording depends on the placement of "filesDescription" in the prompt
   * Prompts: initial prompt given to AI
     * Write "gameDescription"/"fileDescription" in the prompt for replacement with the chosen Game Description/File Description (respectively)
### 4. Run "gameAnalysis.py" and check the "responses" folder. Modify "config.json" as needed.