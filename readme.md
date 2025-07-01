# INSTRUCTIONS

### 1. Run 'gameAnalysis.py'
### 2. Place contextual files in 'filesForAnalysis'
   * Files MUST be in PDF/TXT/HTML/CSV/XML format
### 3. Modify 'config.json'. Or just run 'gameAnalysis.py' (it will ask for the input of missing data).
   * **MUST BE CHANGED** (provides context to the AI):
     * gameDescription: brief description of the game (e.g., "This is a casual mobile game in which players must sort jumbled characters to form words.")
       * Wording depends on the placement of "gameDescription" in the prompt
     * filesDescription: extremely brief description on the contents of each file (e.g., "RAW Game Data Sheets - Level Data.csv: contents of each level")
       * Wording depends on the placement of "filesDescription" in the prompt
   * Change these if you know what you're doing:
     * prompt: initial prompt given to AI
       * Write GAMEDESC in the prompt for replacement with gameDescription
       * Write FILESDESC in the prompt for replacement with fileDescription
     * extraContent: Extra information added to the end of the AI query
### 4. Run 'gameAnalysis.py' and check the 'responses' folder. Modify 'config.json' as needed.