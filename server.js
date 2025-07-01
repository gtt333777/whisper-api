
const express = require('express');
const bodyParser = require('body-parser');
const { exec } = require('child_process');

const app = express();
app.use(bodyParser.json());

app.post('/convert', (req, res) => {
  const { mp3Url, outputName } = req.body;
  if (!mp3Url || !outputName) {
    return res.status(400).json({ error: 'Missing mp3Url or outputName' });
  }

  exec(`python3 convert.py "${mp3Url}" "${outputName}"`, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error: ${error.message}`);
      return res.status(500).json({ error: error.message });
    }
    if (stderr) console.error(`Stderr: ${stderr}`);
    console.log(`Stdout: ${stdout}`);
    res.json({ message: 'Conversion started, check Firebase for MIDI output.' });
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
