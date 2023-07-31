echo "Saving the original Exilence handle..."
reg export HKEY_CLASSES_ROOT\exilence exilence_handle_bkp.reg
echo "Done. To restore Exilence, just double-click on exilence_handle_bkp.reg"
SET wd=%cd%
reg add HKEY_CLASSES_ROOT\exilence\shell\open\command /ve /d "\"%wd%\StashTabExporter.exe\" \"%%1\"" /f