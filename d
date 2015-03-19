[1mdiff --git a/.idea/Worker.iml b/.idea/Worker.iml[m
[1mindex d0876a7..a34a857 100644[m
[1m--- a/.idea/Worker.iml[m
[1m+++ b/.idea/Worker.iml[m
[36m@@ -5,4 +5,5 @@[m
     <orderEntry type="inheritedJdk" />[m
     <orderEntry type="sourceFolder" forTests="false" />[m
   </component>[m
[31m-</module>[m
\ No newline at end of file[m
[32m+[m[32m</module>[m
[41m+[m
[1mdiff --git a/.idea/encodings.xml b/.idea/encodings.xml[m
[1mindex d821048..e206d70 100644[m
[1m--- a/.idea/encodings.xml[m
[1m+++ b/.idea/encodings.xml[m
[36m@@ -1,4 +1,5 @@[m
 <?xml version="1.0" encoding="UTF-8"?>[m
 <project version="4">[m
   <component name="Encoding" useUTFGuessing="true" native2AsciiForPropertiesFiles="false" />[m
[31m-</project>[m
\ No newline at end of file[m
[32m+[m[32m</project>[m
[41m+[m
[1mdiff --git a/.idea/misc.xml b/.idea/misc.xml[m
[1mindex 402a3fd..6d4a587 100644[m
[1m--- a/.idea/misc.xml[m
[1m+++ b/.idea/misc.xml[m
[36m@@ -1,4 +1,5 @@[m
 <?xml version="1.0" encoding="UTF-8"?>[m
 <project version="4">[m
   <component name="ProjectRootManager" version="2" project-jdk-name="Python 2.5.6 (/System/Library/Frameworks/Python.framework/Versions/2.5/bin/python2.5)" project-jdk-type="Python SDK" />[m
[31m-</project>[m
\ No newline at end of file[m
[32m+[m[32m</project>[m
[41m+[m
[1mdiff --git a/.idea/modules.xml b/.idea/modules.xml[m
[1mindex 467ccee..8e9c932 100644[m
[1m--- a/.idea/modules.xml[m
[1m+++ b/.idea/modules.xml[m
[36m@@ -5,4 +5,5 @@[m
       <module fileurl="file://$PROJECT_DIR$/.idea/Worker.iml" filepath="$PROJECT_DIR$/.idea/Worker.iml" />[m
     </modules>[m
   </component>[m
[31m-</project>[m
\ No newline at end of file[m
[32m+[m[32m</project>[m
[41m+[m
[1mdiff --git a/.idea/vcs.xml b/.idea/vcs.xml[m
[1mindex 94a25f7..c80f219 100644[m
[1m--- a/.idea/vcs.xml[m
[1m+++ b/.idea/vcs.xml[m
[36m@@ -3,4 +3,5 @@[m
   <component name="VcsDirectoryMappings">[m
     <mapping directory="$PROJECT_DIR$" vcs="Git" />[m
   </component>[m
[31m-</project>[m
\ No newline at end of file[m
[32m+[m[32m</project>[m
[41m+[m
[1mdiff --git a/.idea/workspace.xml b/.idea/workspace.xml[m
[1mnew file mode 100644[m
[1mindex 0000000..b5a6cab[m
[1m--- /dev/null[m
[1m+++ b/.idea/workspace.xml[m
[36m@@ -0,0 +1,244 @@[m
[32m+[m[32m<?xml version="1.0" encoding="UTF-8"?>[m
[32m+[m[32m<project version="4">[m
[32m+[m[32m  <component name="ChangeListManager">[m
[32m+[m[32m    <list default="true" id="385a748a-7b51-41b9-a8aa-24603b15603c" name="Default" comment="">[m
[32m+[m[32m      <change type="MODIFICATION" beforePath="$PROJECT_DIR$/.idea/Worker.iml" afterPath="$PROJECT_DIR$/.idea/Worker.iml" />[m
[32m+[m[32m      <change type="MODIFICATION" beforePath="$PROJECT_DIR$/.idea/encodings.xml" afterPath="$PROJECT_DIR$/.idea/encodings.xml" />[m
[32m+[m[32m      <change type="MODIFICATION" beforePath="$PROJECT_DIR$/.idea/misc.xml" afterPath="$PROJECT_DIR$/.idea/misc.xml" />[m
[32m+[m[32m      <change type="MODIFICATION" beforePath="$PROJECT_DIR$/.idea/modules.xml" afterPath="$PROJECT_DIR$/.idea/modules.xml" />[m
[32m+[m[32m      <change type="MODIFICATION" beforePath="$PROJECT_DIR$/.idea/vcs.xml" afterPath="$PROJECT_DIR$/.idea/vcs.xml" />[m
[32m+[m[32m      <change type="MODIFICATION" beforePath="$PROJECT_DIR$/worker.py" afterPath="$PROJECT_DIR$/worker.py" />[m
[32m+[m[32m      <change type="MODIFICATION" beforePath="$PROJECT_DIR$/worker_model.py" afterPath="$PROJECT_DIR$/worker_model.py" />[m
[32m+[m[32m      <change type="MODIFICATION" beforePath="$PROJECT_DIR$/worker_util.py" afterPath="$PROJECT_DIR$/worker_util.py" />[m
[32m+[m[32m    </list>[m
[32m+[m[32m    <ignored path="Worker.iws" />[m
[32m+[m[32m    <ignored path=".idea/workspace.xml" />[m
[32m+[m[32m    <option name="TRACKING_ENABLED" value="true" />[m
[32m+[m[32m    <option name="SHOW_DIALOG" value="false" />[m
[32m+[m[32m    <option name="HIGHLIGHT_CONFLICTS" value="true" />[m
[32m+[m[32m    <option name="HIGHLIGHT_NON_ACTIVE_CHANGELIST" value="false" />[m
[32m+[m[32m    <option name="LAST_RESOLUTION" value="IGNORE" />[m
[32m+[m[32m  </component>[m
[32m+[m[32m  <component name="ChangesViewManager" flattened_view="true" show_ignored="false" />[m
[32m+[m[32m  <component name="CreatePatchCommitExecutor">[m
[32m+[m[32m    <option name="PATCH_PATH" value="" />[m
[32m+[m[32m  </component>[m
[32m+[m[32m  <component name="DaemonCodeAnalyzer">[m
[32m+[m[32m    <disable_hints />[m
[32m+[m[32m  </component>[m
[32m+[m[32m  <component name="ExecutionTargetManager" SELECTED_TARGET="default_target" />[m
[32m+[m[32m  <component name="FavoritesManager">[m
[32m+[m[32m    <favorites_list name="Worker" />[m
[32m+[m[32m  </component>[m
[32m+[m[32m  <component name="FileEditorManager">[m
[32m+[m[32m    <leaf>[m
[32m+[m[32m      <file leaf-file-name="worker.py" pinned="false" current="false" current-in-tab="false">[m
[32m+[m[32m        <entry file="file://$PROJECT_DIR$/worker.py">[m
[32m+[m[32m          <provider selected="true" editor-type-id="text-editor">[m
[32m+[m[32m            <state vertical-scroll-proportion="-8.074074" vertical-offset="6879" max-vertical-offset="13870">[m
[32m+[m[32m              <caret line="385" column="17" selection-start-line="385" selection-start-column="17" selection-end-line="385" selection-end-column="17" />[m
[32m+[m[32m              <folding />[m
[32m+[m[32m            </state>[m
[32m+[m[32m          </provider>[m
[32m+[m[32m        </entry>[m
[32m+[m[32m      </file>[m
[32m+[m[32m      <file leaf-file-name="worker_config_mgr.py" pinned="false" current="false" current-in-tab="false">[m
[32m+[m[32m        <entry file="file://$PROJECT_DIR$/worker_config_mgr.py">[m
[32m+[m[32m          <provider selected="true" editor-type-id="text-editor">[m
[32m+[m[32m            <state vertical-scroll-proportion="-7.6" vertical-offset="0" max-vertical-offset="380">[m
[32m+[m[32m              <caret line="11" column="37" selection-start-line="11" selection-start-column="37" selection-end-line="11" selection-end-column="37" />[m
[32m+[m[32m              <folding />[m
[32m+[m[32m            </state>[m
[32m+[m[32m          </provider>[m
[32m+[m[32m        </entry>[m
[32m+[m[32m      </file>[m
[32m+[m[32m      <file leaf-file-name="worker_util.py" pinned="false" current="true" current-in-tab="true">[m
[32m+[m[32m        <entry file="file://$PROJECT_DIR$/worker_util.py">[m
[32m+[m[32m          <provider selected="true" editor-type-id="text-editor">[m
[32m+[m[32m            <state vertical-scroll-proportion="0.5953039" vertical-offset="3920" max-vertical-offset="6973">[m
[32m+[m[32m              <caret line="236" column="35" selection-start-line="236" selection-start-column="35" selection-end-line="236" selection-end-column="35" />[m
[32m+[m[32m              <folding />[m
[32m+[m[32m            </state>[m
[32m+[m[32m          </provider>[m
[32m+[m[32m        </entry>[m
[32m+[m[32m      </file>[m
[32m+[m[32m      <file leaf-file-name="worker_model.py" pinned="false" current="false" current-in-tab="false">[m
[32m+[m[32m        <entry file="file://$PROJECT_DIR$/worker_model.py">[m
[32m+[m[32m          <provider selected="true" editor-type-id="text-editor">[m
[32m+[m[32m            <state vertical-scroll-proportion="-17.48" vertical-offset="0" max-vertical-offset="1330">[m
[32m+[m[32m              <caret line="28" column="34" selection-start-line="28" selection-start-column="34" selection-end-line="28" selection-end-column="34" />[m
[32m+[m[32m              <folding />[m
[32m+[m[32m            </state>[m
[32m+[m[32m          </provider>[m
[32m+[m[32m        </entry>[m
[32m+[m[32m      </file>[m
[32m+[m[32m    </leaf>[m
[32m+[m[32m  </component>[m
[32m+[m[32m  <component name="FindManager">[m
[32m+[m[32m    <FindUsagesManager>[m
[32m+[m[32m      <setting name="OPEN_NEW_TAB" value="true" />[m
[32m+[m[32m 