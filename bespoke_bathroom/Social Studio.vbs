' Bespoke Bathroom UK - Social Studio (Windows): double-click to open the studio.
' Runs launch.mjs with no console window: it starts the server in the background if
' needed, then opens the studio in Chrome.
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
here = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = here
On Error Resume Next
shell.Run "node """ & here & "\launch.mjs""", 0, False
If Err.Number <> 0 Then
  MsgBox "Node.js is not installed. Download the LTS version from https://nodejs.org, then try again.", 48, "Social Studio"
End If
