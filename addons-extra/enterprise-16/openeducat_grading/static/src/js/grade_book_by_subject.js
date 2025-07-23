odoo.define('openeducat_grading.grade_book_grid_by_subject', function(require) {
    "use strict";

    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var viewRegistry = require('web.view_registry');
    var _t = core._t;
    var QWeb = core.qweb;
    var utils = require('web.utils');
    var config = require('web.config');
    var time = require('web.time');
    var Widget = require('web.Widget');
    var ajax = require('web.ajax');
    var framework = require('web.framework');

    var GradeBookBySubject = AbstractAction.extend({
        hasControlPanel: true,
        title: core._t('GradeBook'),
        jsLibs: [
            '/openeducat_grading/static/src/js/handsontable.full.min.js',
        ],
        cssLibs: [
            '/openeducat_grading/static/src/css/handsontable.full.min.css',
        ],
        events:{
            'change #grid_view_drop_down': '_onChangeDropDown',
            'change #student_selection': '_onChangeStudent',
            'click #export_csv': '_ExportCSV',
            'click #assignment_toggle': '_ToggleAssignment',
        },
        init: function(parent, state, params) {
            this._super.apply(this, arguments);
            this.student_progression_id = state.params.grade_book;
        },
        start: function() {
            var self = this;
            this.$buttons = $(QWeb.render('export_button_template'));
            this.assignmentDetails = true;
            this._rpc({
                model: "op.student.progression",
                method: "get_student_data_grade_book_by_student",
                args: [this.student_progression_id],
            }).then(function(data){
                self.allRender(self.student_progression_id);
            });
            return this._super();
        },
        _onChangeDropDown: function(e){
            var currentValue = $(e.currentTarget).val();
            this.$GridBookContainer.unwrap();
            this.$GridBookContainer.remove();
            this.$CommentContainer.unwrap();
            this.$CommentContainer.remove();
            var student_id = $('#student_selection').val();
            if(student_id == ''){
                this.allRender(this.student_progression_id);
            }else{
                this.allRender(student_id);
            }
        },
        _onChangeStudent:function(e){
            var self = this;
            var currentId = $(e.currentTarget).val();
            this.$GridBookContainer.unwrap();
            this.$GridBookContainer.remove();
//            this.$CommentContainer.unwrap();
//            this.$CommentContainer.remove();
            if(currentId == ''){
                this.allRender(this.student_progression_id);
            }else{
                this.allRender(currentId);
            }
        },
        allRender: function(currentId){
            var self = this;
            framework.blockUI();
            this._rpc({
                model: "op.subject",
                method: "get_grade_book_grid_data_by_subject",
                args: [parseInt(currentId)],
            }).then(function(data){
                self.grade_book_data = JSON.parse(data['data']);
                if(Object.keys(self.grade_book_data).length == 0){
                    self.$el.find('.o_content').append(QWeb.render('grade_book_no_data_template'));
                }else{
                    var dropDownValue = self.$el.find("#grid_view_drop_down").val();
                    self._renderAssignmentWise(self.grade_book_data,data['credit'],data['subject'],data['subject_code']);
                }
                self.$el.find('.o_cp_buttons').append(self.$buttons);
            }).then(function (){
                framework.unblockUI();
            });
        },
        _ToggleAssignment: function(e){
            if($(e.currentTarget).is(":checked")){
                this.assignmentDetails = true;
            }else{
                this.assignmentDetails = false;
            }
            this.$GridBookContainer.empty();
            this.allRender(this.student_progression_id);
        },
        _ExportCSV:function(){
            var hot = this.$GridBookContainer.handsontable('getInstance');
            const exportPlugin = hot.getPlugin('exportFile');
            hot.updateSettings({
                hiddenRows: {
                    rows: [],
                    indicators: true
                }
            });
            exportPlugin.downloadFile('csv', {
                bom: false,
                filename: 'GradeBook',
                exportHiddenColumns: true,
                exportHiddenRows: true,
                mimeType: 'text/csv',
                columnHeaders: true,
            });
            hot.getPlugin('nestedRows').collapsingUI.collapseAll();
        },
        _renderAssignmentWise: function(grade_data, creditBool, name, code){
            var grid_data = grade_data;
            var self = this;
            this.QuarterTermBool = false;
            this.creditAvailable = creditBool;
            this.attendanceAvailable = false;
            var $GridBookContainer = $(QWeb.render('grade_book_widget_template'));
            this.$GridBookContainer = $GridBookContainer;
            this.$el.find('.o_content').append($GridBookContainer);
            if(this.$el.find('.grade_table').length == 0){
                this.$el.find('.o_content').append($GridBookContainer);
                $GridBookContainer.wrap('<div class="new-parent grade_table p-3"></div>');
            }else{
                this.$el.find('.grade_table').append($GridBookContainer);
            }
            var data = [];
            var dataLength = Object.keys(grid_data).length;
            var objectData = Object.keys(grid_data);
            var ColumnHeaders = ["Student","Year","Semester","Quarter","Code","Subject","Name","Grade","Credit","GPA","Obtained","Final Grades"];
            for(var i=0; i< dataLength; i++){
                var studentData = {};
                studentData['Student'] = objectData[i];
                var yearDataLength = Object.keys(grid_data[objectData[i]]).length;
                var yearDataKeys = Object.keys(grid_data[objectData[i]]);
                var yearDataData = grid_data[objectData[i]];
                this.QuarterTermBool = yearDataData.Quarter_term;
                studentData['__children'] = [];
                for(var j=0; j< yearDataLength; j++){
                    var finaTermData = {};
                    if(this.QuarterTermBool){
                        if(typeof(yearDataData[yearDataKeys[j]]) == 'object'){
                            finaTermData['Year'] = yearDataKeys[j];
                            finaTermData['__children'] = [];
                            var termDataKeys = Object.keys(yearDataData[yearDataKeys[j]]);
                            var termDataLength = Object.keys(yearDataData[yearDataKeys[j]]).length;
                            var termDataData = yearDataData[yearDataKeys[j]];
                            for(var te = 0; te < termDataLength; te ++){
                                if(termDataKeys[te].includes('Year Total') == false && termDataKeys[te].includes('Grade') == false && termDataKeys[te].includes('override') == false){
                                    var semesterData = {};
                                    semesterData['Semester'] = termDataKeys[te];
                                    if(this.creditAvailable){
                                        semesterData['Grade'] = termDataData[termDataKeys[te]].Grade;
                                    }
                                    if(termDataData[termDataKeys[te]].hasOwnProperty('GPA')){
                                        semesterData['GPA'] = termDataData[termDataKeys[te]].GPA;
                                    }
                                    semesterData['Obtained'] = termDataData[termDataKeys[te]].Total;
                                    if(termDataData[termDataKeys[te]].hasOwnProperty('override')){
                                        semesterData['Final Grades'] = termDataData[termDataKeys[te]].override;
                                    }
                                    if(typeof(termDataData[termDataKeys[te]]) == 'object'){
                                        var QuarterDataLength = Object.keys(termDataData[termDataKeys[te]]).length;
                                        var QuarterDataKeys = Object.keys(termDataData[termDataKeys[te]]);
                                        var QuarterDataData = termDataData[termDataKeys[te]];
                                        semesterData['__children'] = [];
                                        for(var k=0; k<QuarterDataLength; k++){
                                            var quarterData = {};
                                            if(typeof(QuarterDataData[QuarterDataKeys[k]]) == 'object' && QuarterDataData[QuarterDataKeys[k]].hasOwnProperty(name)){
                                                quarterData['Quarter'] = QuarterDataKeys[k];
                                                if(this.creditAvailable){
                                                    quarterData['Grade'] = QuarterDataData[QuarterDataKeys[k]].Grade;
                                                }
                                                quarterData['Obtained'] = QuarterDataData[QuarterDataKeys[k]].Total;
                                                if(QuarterDataData[QuarterDataKeys[k]].hasOwnProperty('override')){
                                                    quarterData['Final Grades'] = QuarterDataData[QuarterDataKeys[k]].override;
                                                }
                                                var subjectLength = Object.keys(QuarterDataData[QuarterDataKeys[k]]).length;
                                                var subjectKeys = Object.keys(QuarterDataData[QuarterDataKeys[k]]);
                                                var subjectData = QuarterDataData[QuarterDataKeys[k]];
                                                quarterData['__children'] = [];
                                                for(var l=0;l< subjectLength; l++){
                                                    var subjectDataData = {};
                                                    if(typeof(subjectData[subjectKeys[l]]) == 'object'){
                                                        if(subjectData[subjectKeys[l]].hasOwnProperty('Credit')){
                                                            this.creditAvailable = true;
                                                        }
                                                        subjectDataData['Code'] = subjectData[subjectKeys[l]].Code;
                                                        subjectDataData['Subject'] = subjectKeys[l];
                                                        if(this.creditAvailable){
                                                            subjectDataData['Grade'] = subjectData[subjectKeys[l]].Grade;
                                                            subjectDataData['Credit'] = subjectData[subjectKeys[l]].Credit;
                                                        }
                                                        subjectDataData['Obtained'] = subjectData[subjectKeys[l]].Mark;
                                                        if(subjectData[subjectKeys[l]].hasOwnProperty('override')){
                                                            subjectDataData['Final Grades'] = subjectData[subjectKeys[l]].override;
                                                        }
                                                        var assignmentLength = Object.keys(subjectData[subjectKeys[l]].Assignment).length;
                                                        var assignmentKeys = Object.keys(subjectData[subjectKeys[l]].Assignment);
                                                        var assignmentData = subjectData[subjectKeys[l]].Assignment;
                                                        subjectDataData['__children'] = [];
                                                        if(this.assignmentDetails){
                                                            for(var y=0; y < assignmentLength; y++){
                                                                var assignmentDict = {};
                                                                assignmentDict['Name'] = assignmentKeys[y];
                                                                if(this.creditAvailable){
                                                                    assignmentDict['Obtained'] = assignmentData[assignmentKeys[y]].Mark;
                                                                    assignmentDict['Grade'] = assignmentData[assignmentKeys[y]].Grade;
                                                                }else{
                                                                    assignmentDict['Obtained'] = assignmentData[assignmentKeys[y]];
                                                                }
                                                                subjectDataData['__children'].push(assignmentDict);
                                                            }
                                                        }
                                                        quarterData['__children'].push(subjectDataData);
                                                    }else{
                                                        if(subjectKeys[l] != 'Comment' && subjectKeys[l] != 'Total'){
                                                            if(subjectKeys[l] == 'Attendance'){
                                                                this.attendanceAvailable = true;
                                                                if(subjectData[subjectKeys[l]] != ""){
                                                                    quarterData['__children'].splice(0, 0,{
                                                                        "Subject": "Attendance",
                                                                        "Obtained": subjectData[subjectKeys[l]],
                                                                    });
                                                                }
                                                            }
                                                            if(subjectKeys[l] == "GPA"){
                                                                //quarterData['GPA'] = subjectData[subjectKeys[l]];
                                                            }
                                                        }
                                                    }
                                                }
                                                semesterData['__children'].push(quarterData);
                                            }
                                        }
                                    }
                                    finaTermData['__children'].push(semesterData);
                                }else{
                                    finaTermData['Semester'] = null;
                                    finaTermData['Quarter'] = null;
                                    finaTermData['Code'] = null;
                                    finaTermData['Subject'] = null;
                                    if(this.assignmentDetails){
                                        finaTermData['Name'] = null;
                                    }
                                    if(this.creditAvailable){
                                        finaTermData['Grade'] = termDataData.Grade;
                                        finaTermData['Credit'] = null;
                                        finaTermData['GPA'] = null;
                                    }
                                    finaTermData['Obtained'] = termDataData['Year Total'];
                                    if(termDataData.hasOwnProperty('override')){
                                        finaTermData['Final Grades'] = termDataData['override'];
                                    }else{
                                        finaTermData['Final Grades'] = null;
                                    }
                                }
                            }
                        }
                        if(Object.keys(finaTermData).length > 0){
                            studentData['__children'].push(finaTermData);
                        }
                    }else{
                        if(typeof(yearDataData[yearDataKeys[j]]) == 'object'){
                            finaTermData['Year'] = yearDataKeys[j];
                            finaTermData['__children'] = [];
                            var termDataKeys = Object.keys(yearDataData[yearDataKeys[j]]);
                            var termDataLength = Object.keys(yearDataData[yearDataKeys[j]]).length;
                            var termDataData = yearDataData[yearDataKeys[j]];
                            for(var te = 0; te < termDataLength; te ++){
                                if(termDataKeys[te].includes('Year Total') == false && termDataKeys[te].includes('Grade') == false && termDataKeys[te].includes('override') == false && termDataData[termDataKeys[te]].hasOwnProperty(name)){
                                    var semesterData = {};
                                    semesterData['Semester'] = termDataKeys[te];
                                    if(this.creditAvailable){
                                        semesterData['Grade'] = termDataData[termDataKeys[te]].Grade;
                                    }
                                    semesterData['Obtained'] = termDataData[termDataKeys[te]].Total;
                                    if(termDataData[termDataKeys[te]].hasOwnProperty('override')){
                                        semesterData['Final Grades'] = termDataData[termDataKeys[te]].override;
                                    }
                                    semesterData['__children'] = [];
                                    if(typeof(termDataData[termDataKeys[te]]) == 'object'){
                                        var subjectLength = Object.keys(termDataData[termDataKeys[te]]).length;
                                        var subjectKeys = Object.keys(termDataData[termDataKeys[te]]);
                                        var subjectData = termDataData[termDataKeys[te]];
                                        for(var w=0; w< subjectLength; w++){
                                            if(typeof(subjectData[subjectKeys[w]]) == 'object'){
                                                var subjectDataData = {};
                                                if(subjectData[subjectKeys[w]].hasOwnProperty('Credit')){
                                                        this.creditAvailable = true;
                                                }
                                                subjectDataData['Code'] = subjectData[subjectKeys[w]].Code;
                                                subjectDataData['Subject'] = subjectKeys[w];
                                                if(this.creditAvailable){
                                                    subjectDataData['Grade'] = subjectData[subjectKeys[w]].Grade;
                                                    subjectDataData['Credit'] = subjectData[subjectKeys[w]].Credit;
                                                }
                                                subjectDataData['Obtained'] = subjectData[subjectKeys[w]].Mark;
                                                if(subjectData[subjectKeys[w]].hasOwnProperty('override')){
                                                    subjectDataData['Final Grades'] = subjectData[subjectKeys[w]].override;
                                                }
                                                var assignmentLength = Object.keys(subjectData[subjectKeys[w]].Assignment).length;
                                                var assignmentKeys = Object.keys(subjectData[subjectKeys[w]].Assignment);
                                                var assignmentData = subjectData[subjectKeys[w]].Assignment;
                                                subjectDataData['__children'] = [];
                                                if(this.assignmentDetails){
                                                    for(var y=0; y < assignmentLength; y++){
                                                        var assignmentDict = {};
                                                        assignmentDict['Name'] = assignmentKeys[y];
                                                        if(this.creditAvailable){
                                                            assignmentDict['Obtained'] = assignmentData[assignmentKeys[y]].Mark;
                                                            assignmentDict['Grade'] = assignmentData[assignmentKeys[y]].Grade;
                                                        }else{
                                                            assignmentDict['Obtained'] = assignmentData[assignmentKeys[y]];
                                                        }
                                                        subjectDataData['__children'].push(assignmentDict);
                                                    }
                                                }
                                                semesterData['__children'].push(subjectDataData);
                                            }else{
                                                if(subjectKeys[w] != 'Comment' && subjectKeys[w] != 'Total'){
                                                    if(subjectKeys[w] == 'Attendance'){
                                                        this.attendanceAvailable = true;
                                                        if(subjectData[subjectKeys[w]] != ""){
                                                            semesterData['__children'].splice(0, 0,{
                                                                "Subject": "Attendance",
                                                                "Obtained": subjectData[subjectKeys[w]],
                                                            });
                                                        }
                                                    }
                                                    if(subjectKeys[w] == "GPA"){
                                                        semesterData['GPA'] = subjectData[subjectKeys[w]];
                                                    }
                                                }
                                            }
                                        }
                                    }
                                    finaTermData['__children'].push(semesterData);
                                }else{
                                    finaTermData['Semester'] = null;
                                    finaTermData['Code'] = null;
                                    finaTermData['Subject'] = null;
                                    if(this.assignmentDetails){
                                        finaTermData['Name'] = null;
                                    }
                                    if(this.creditAvailable){
                                        finaTermData['Grade'] = termDataData['Grade'];
                                        finaTermData['Credit'] = null;
                                        finaTermData['GPA'] = null;
                                    }
                                    finaTermData['Obtained'] = termDataData['Year Total'];
                                    if(termDataData.hasOwnProperty('override')){
                                        finaTermData['Final Grades'] = termDataData['override'];
                                    }else{
                                        finaTermData['Final Grades'] = null;
                                    }
                                }
                            }
                        }
                        if(Object.keys(finaTermData).length > 0){
                            studentData['__children'].push(finaTermData);
                        }
                    }
                    studentData['Year'] = null;
                    studentData['Semester'] = null;
                    if(this.QuarterTermBool){
                        studentData['Quarter'] = null;
                    }
                    studentData['Code'] = null;
                    studentData['Subject'] = null;
                    if(this.assignmentDetails){
                        studentData['Name'] = null;
                    }
                    if(this.creditAvailable){
                        studentData['Grade'] = null;
                        studentData['Credit'] = null;
                        studentData['GPA'] = null;
                    }
                    studentData['Obtained'] = null;
                    studentData['Final Grades'] = null;
                }
                data.push(studentData);
            }
            if(this.QuarterTermBool){
                if(!this.creditAvailable){
                    ColumnHeaders.splice(ColumnHeaders.indexOf("GPA"), 1);
                    ColumnHeaders.splice(ColumnHeaders.indexOf("Grade"), 1);
                    ColumnHeaders.splice(ColumnHeaders.indexOf("Credit"), 1);
                }
            }else{
                ColumnHeaders.splice(ColumnHeaders.indexOf("Quarter"), 1);
                if(!this.creditAvailable){
                    ColumnHeaders.splice(ColumnHeaders.indexOf("GPA"), 1);
                    ColumnHeaders.splice(ColumnHeaders.indexOf("Grade"), 1);
                    ColumnHeaders.splice(ColumnHeaders.indexOf("Credit"), 1);
                }
            }
            if(data != false){
                if(!this.QuarterTermBool){
                    for(var q = data.length - 1; q >= 0; q--){
                        if(data[q].__children.length == 0){
                            data.splice(q, 1);
                        }else{
                            var terms = data[q].__children;
                            for(var term = terms.length - 1; term >= 0;term-- ){
                                if(terms[term].__children.length == 0){
                                    terms.splice(term, 1);
                                }
                            }
                            if(data[q].__children.length == 0){
                                data.splice(q, 1);
                            }
                        }
                    }
                }else{
                    for(var q = data.length - 1; q >= 0; q--){
                        for(var p = data[q].__children.length - 1; p >= 0; p-- ){
                            var sub_data = data[q].__children;
                            if(sub_data[p].__children.length == 0){
                                sub_data.splice(p, 1);
                            }else{
                                var semesters = sub_data[p].__children;
                                for(var semester = semesters.length - 1; semester >= 0; semester--){
                                    if(semesters[semester].__children.length == 0){
                                        semesters.splice(semester, 1);
                                    }
                                }
                            }
                            if(sub_data[p].__children.length == 0){
                                sub_data.splice(p, 1);
                            }
                        }
                    }
                }
            }
            if(!this.assignmentDetails){
                ColumnHeaders.splice(ColumnHeaders.indexOf("Name"), 1);
            }
            $GridBookContainer.handsontable({
                data: data,
                colHeaders: ColumnHeaders,
                contextMenu: false,
                editor: false,
                disableVisualSelection: true,
                rowHeaders: true,
                nestedRows: true,
                licenseKey: 'non-commercial-and-evaluation',
                className: "htCenter",
            });
            var hotInstance = $GridBookContainer.handsontable('getInstance');
            hotInstance.getPlugin('nestedRows').collapsingUI.collapseAll();
            setTimeout(function(){ hotInstance.render(); },10);
        },
    });
    core.action_registry.add('grade_book_grid_by_subject', GradeBookBySubject);

    return GradeBookBySubject;
});
