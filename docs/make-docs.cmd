@echo off
@cd ..\design
@call .\make-docs.cmd
@copy *.html ..\docs /y
@copy *.png ..\docs /y
@cd ..\AdaptiveModelingWorkflowApi\docs
@call .\make-docs.cmd
@copy *.html ..\..\docs /y
@cd ..\..\ModelUpdateApi\docs
@call .\make-docs.cmd
@copy *.html ..\..\docs /y
@cd ..\..\docs
@IF NOT EXIST .\css MKDIR css
@ROBOCOPY /NS /NC /NFL /NDL /NP /NJH /NJS /S /MIR ..\docs-support\css .\css
@IF NOT EXIST .\js MKDIR js
@ROBOCOPY /NS /NC /NFL /NDL /NP /NJH /NJS /S /MIR ..\docs-support\js .\js
@IF NOT EXIST .\styles MKDIR styles
@ROBOCOPY /NS /NC /NFL /NDL /NP /NJH /NJS /S /MIR ..\docs-support\styles .\styles
