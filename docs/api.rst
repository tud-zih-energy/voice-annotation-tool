API
===

The voice-annotation-tool package also includes an API to load, modify and save CommonVoice datasets.

.. code-block::
   :caption: Loading a TSV file using the Project class

   from voice_annotation_tool.project import Project
   
   # Create a new project.
   project = Project()
   
   # Load a TSV file.
   with open('tsv_file.tsv') as file:
       project.load_tsv(file)
   
   # Show all annotations.
   print(project.annotations)

.. code-block::
   :caption: Changing the sentence and votes of an annotation

   from voice_annotation_tool.project import Project
   from voice_annotation_tool.annotation import Annotation
   
   project = Project()
   project.load_audio_files(Path('audio'))

   annotation = project.annotations[0]
   annotation.sentence = 'Annotated text'
   annotation.age = 'thirties'
   annotation.up_votes += 1

   with open('tsv_file.tsv', 'w', newline='') as file:
       project.save_annotations(file)
