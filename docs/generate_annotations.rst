Automatic Annotation Generation
===============================

To speed up annotation, Coqui's speech-to-text capabilities can be used to automatically generate annotations for the samples.

Install FFmpeg
--------------

If you don't have it already, install FFmpeg on your machine. It is required to prepare the audio files so that they can be used by Coqui.

**Windows: Use Chocolatey or download it from `here <https://www.ffmpeg.org/download.html>`_**

**Linux: Use your package manager of choice.**

Download a Language Model
-------------------------

If you don't want to train your own model, you can download a pre-trained one from the official Coqui website: https://coqui.ai/models.

Generate Annotations
--------------------

First, select your language model under `Edit>Select Language Model...`. Then choose `Edit>Auto-Generate Annotation Text` and wait for the process to complete. A popup will be shown once the it is finished.
