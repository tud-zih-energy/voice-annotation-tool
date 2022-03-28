Import and Export
=================

The annotations can be exported and imported in multiple formats, including Json and CSV.

These are meant for easy reading and modification by other applications, and only include the sample file name and the annotated text.

Json
----

.. code-block::
   :caption: An example of an exported Json file

   [
     {
       "file": "sample1.mp3",
       "text": "Annotation One",
     },
     {
       "file": "sample2.mp3",
       "text": "Annotation Two",
     }
   ]

CSV
---

.. code-block::
   :caption: An example of an exported CSV file

   file;text
   sample1.mp3;Annotation One
   sample2.mp3;Annotation Two

