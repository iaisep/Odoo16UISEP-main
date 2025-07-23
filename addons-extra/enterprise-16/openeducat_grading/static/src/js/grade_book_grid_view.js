odoo.define('openeducat_grading.grade_book_grid_view', function(require) {
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

    var GridGradeBook = AbstractAction.extend({
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
            this.is_gradebook = state.params.is_gradebook;
        },
        start: function() {
            var self = this;
            this.$buttons = $(QWeb.render('export_button_template'));
            this.assignmentDetails = true;
            this._rpc({
                model: "op.student.progression",
                method: "get_student_data_grade_book",
                args: [this.student_progression_id],
            }).then(function(data){
                var $studentDropDown = $(QWeb.render('student_selection_template'));
                self.$el.find('.o_content').append($studentDropDown);
                for(var d=0; d < data.length; d++){
                    self.$el.find('#student_selection').append("<option value="+data[d].id+" >"+data[d].name+"</option>");
                }
                var $dropDown = $(QWeb.render('grade_book_view_drop_down'));
                self.$el.find('.o_content').append($dropDown);
                var dropDownValue = self.$el.find("#grid_view_drop_down").val();
                self.allRender(self.student_progression_id);
            });
            return this._super();
        },
        _ToggleAssignment: function(e){
            if($(e.currentTarget).is(":checked")){
                this.assignmentDetails = true;
            }else{
                this.assignmentDetails = false;
            }
            $('.grade_table').remove();
            this.$CommentContainer.empty();
            this.allRender(this.student_progression_id);
        },
        _ExportCSV:function(){
            $('.grade_table').each( function(){
                var hot = $(this).find('> div').handsontable('getInstance');
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
            });
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
            this.$CommentContainer.unwrap();
            this.$CommentContainer.remove();
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
                model: "gradebook.gradebook",
                method: "get_grade_book_grid_data",
                args: [false, parseInt(currentId), this.is_gradebook],
            }).then(function(data){
                if(data != false){
                     self.grade_book_data = JSON.parse(data['data']);
                     self._renderAssignmentWise(self.grade_book_data, data['credit']);
                        self._renderCommentTable(self.grade_book_data);
                }else{
                    self.$el.find('.o_content').append(QWeb.render('grade_book_no_data_template'));
                }
                self.$el.find('.o_cp_buttons').append(self.$buttons);
            }).then(function (){
                framework.unblockUI();
            });
        },
        _renderCommentTable: function(grade_data){
            var grid_data = grade_data;
            this.QuarterTermBool = false;
            var self = this;
            var $CommentContainer = $(QWeb.render('grade_book_comment_table_template'));
            this.$CommentContainer = $CommentContainer;
            if(this.$el.find('.comment-table').length == 0){
                this.$el.find('.o_content').append($CommentContainer);
                $CommentContainer.wrap('<div class="new-parent comment-table p-3"></div>');
            }else{
                this.$el.find('.grade_table').append($CommentContainer);
            }
            var lastHeaders = [];
            var lastData = [];
            var lastDataDict = {};
            var commentData = [];
            var CommentHeaders = ["Year","Subject","Term","Comment"]
            var data = [];
            var dataLength = Object.keys(grid_data).length;
            var objectData = Object.keys(grid_data);
            var yearData = {};
            yearData['__children'] = [];
            for(var i=0; i< dataLength; i++){
                var studentData = {};
                studentData['Course'] = objectData[i];
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
                                    if(termDataData[termDataKeys[te]].hasOwnProperty("Comment")){
                                        commentData.push({
                                           "Year": yearDataKeys[j],
                                           "Subject": null,
                                           "Term": termDataKeys[te],
                                           "Comment": termDataData[termDataKeys[te]].Comment,

                                        });
                                    }
                                    var semesterData = {};
                                    semesterData['Semester'] = termDataKeys[te];
                                    if(this.creditAvailable){
                                        semesterData['Grade'] = termDataData[termDataKeys[te]].Grade;
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
                                            if(typeof(QuarterDataData[QuarterDataKeys[k]]) == 'object'){
                                                quarterData['Quarter'] = QuarterDataKeys[k];
                                                if(QuarterDataData[QuarterDataKeys[k]].hasOwnProperty("Comment")){
                                                    commentData.push({
                                                       "Year": yearDataKeys[j],
                                                       "Subject": null,
                                                       "Term": QuarterDataKeys[k],
                                                       "Comment": QuarterDataData[QuarterDataKeys[k]].Comment,

                                                    });
                                                }
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
                                                        if(subjectData[subjectKeys[l]].hasOwnProperty("Comment")){
                                                            commentData.push({
                                                               "Year": yearDataKeys[j],
                                                               "Subject": subjectKeys[l],
                                                               "Term": QuarterDataKeys[k],
                                                               "Comment": subjectData[subjectKeys[l]].Comment,

                                                            });
                                                        }
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
                                                                quarterData['GPA'] = subjectData[subjectKeys[l]];
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
                        studentData['__children'].push(finaTermData)
                    }else{
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
                                    semesterData['Obtained'] = termDataData[termDataKeys[te]].Total;
                                    if(termDataData[termDataKeys[te]].hasOwnProperty('override')){
                                        semesterData['Final Grades'] = termDataData[termDataKeys[te]].override;
                                    }
                                    if(termDataData[termDataKeys[te]].hasOwnProperty("Comment")){
                                        commentData.push({
                                           "Year": yearDataKeys[j],
                                           "Subject": null,
                                           "Term": termDataKeys[te],
                                           "Comment": termDataData[termDataKeys[te]].Comment,

                                        });
                                    }
                                    semesterData['__children'] = [];
                                    if(typeof(termDataData[termDataKeys[te]]) == 'object'){
                                        var subjectLength = Object.keys(termDataData[termDataKeys[te]]).length;
                                        var subjectKeys = Object.keys(termDataData[termDataKeys[te]]);
                                        var subjectData = termDataData[termDataKeys[te]];
                                        for(var w=0; w< subjectLength; w++){
                                            if(typeof(subjectData[subjectKeys[w]]) == 'object'){
                                                var subjectDataData = {};
                                                if(subjectData[subjectKeys[w]].hasOwnProperty("Comment")){
                                                    commentData.push({
                                                       "Year": yearDataKeys[j],
                                                       "Subject": subjectKeys[w],
                                                       "Term": termDataKeys[te],
                                                       "Comment": subjectData[subjectKeys[w]].Comment,

                                                    });
                                                }
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
                        studentData['__children'].push(finaTermData);
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
            data.push(yearData);
            $CommentContainer.handsontable({
                data: commentData,
                colHeaders: CommentHeaders,
                contextMenu: false,
                editor: false,
                disableVisualSelection: true,
                nestedRows: true,
                licenseKey: 'non-commercial-and-evaluation',
                className: "htCenter",
            });
            var hotInstance = $CommentContainer.handsontable('getInstance');
            setTimeout(function(){ hotInstance.render(); },10);
        },
        _renderAssignmentWise: function(grade_data, creditBool){
            var grid_data = grade_data;
            var self = this;
            this.QuarterTermBool = false;
            this.creditAvailable = creditBool;
            this.attendanceAvailable = false;
            //var $GridBookContainer = $(QWeb.render('grade_book_widget_template'));
            //this.$GridBookContainer = $GridBookContainer;
            //this.$el.find('.o_content').append($GridBookContainer);
//            if(this.$el.find('.grade_table').length == 0){
//                this.$el.find('.o_content').append($GridBookContainer);
//                $GridBookContainer.wrap('<div class="new-parent grade_table p-3"></div>');
//            }else{
//                this.$el.find('.grade_table').append($GridBookContainer);
//            }
            var dataLength = Object.keys(grid_data).length;
            var objectData = Object.keys(grid_data);
            var ColumnHeaders = ["Course","Year","Semester","Quarter","Code","Subject","Name","Grade","Credit","GPA","Obtained","Final Grades"];
            for(var i=0; i< dataLength; i++){
                var studentData = {};
                var data = [];
                var $GridBookContainer = $(QWeb.render('grade_book_widget_template'));
                this.$el.find('.o_content').append($GridBookContainer);
                $GridBookContainer.wrap('<div class="new-parent grade_table p-3" index="' + i + '"></div>');
                studentData['Course'] = objectData[i];
                var yearDataLength = Object.keys(grid_data[objectData[i]]).length;
                var yearDataKeys = Object.keys(grid_data[objectData[i]]);
                var yearDataData = grid_data[objectData[i]];
                this.QuarterTermBool = yearDataData.Quarter_term;
                studentData['__children'] = [];
                for(var j=0; j< yearDataLength; j++){
                    if(this.QuarterTermBool){
                        var finaTermData = {};
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
                                            if(typeof(QuarterDataData[QuarterDataKeys[k]]) == 'object'){
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
                                                        if(this.assignmentDetails){
                                                            subjectDataData['__children'] = [];
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
                        }else{
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
                                studentData['Grade'] = yearDataData.Grade;
                                studentData['Credit'] = null;
                                studentData['GPA'] = null;
                            }
                            studentData['Obtained'] = null;
                            studentData['Final Grades'] = yearDataData.override;
                        }
                        if(!yearDataData.hasOwnProperty("override")){
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
                                studentData['Grade'] =  null;
                                studentData['Credit'] = null;
                                studentData['GPA'] = null;
                            }
                            studentData['Obtained'] = null;
                            studentData['Final Grades'] = null;
                        }
                        if(Object.keys(finaTermData).length > 0){
                            studentData['__children'].push(finaTermData)
                        }
                    }else{
                        var finaTermData = {};
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
                                                if(this.assignmentDetails){
                                                    subjectDataData['__children'] = [];
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
                        }else{
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
                                studentData['Grade'] = yearDataData.Grade;
                                studentData['Credit'] = null;
                                studentData['GPA'] = null;
                            }
                            studentData['Obtained'] = null;
                            studentData['Final Grades'] = yearDataData.override;
                        }
                        if(!yearDataData.hasOwnProperty("override")){
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
                                studentData['Grade'] =  null;
                                studentData['Credit'] = null;
                                studentData['GPA'] = null;
                            }
                            studentData['Obtained'] = null;
                            studentData['Final Grades'] = null;
                        }
                        if(Object.keys(finaTermData).length > 0){
                            studentData['__children'].push(finaTermData);
                        }
                    }

                }
                data.push(studentData);
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
                if(!this.assignmentDetails){
                    ColumnHeaders.splice(ColumnHeaders.indexOf("Name"), 1);
                }
                var NewColumnHeaders = [];
                var columnWidths = [];
                for(var col = 0; col < ColumnHeaders.length; col++){
                    if(col != ColumnHeaders.length - 1){
                        NewColumnHeaders.splice(col, 0, {
                            data: ColumnHeaders[col],
                            readOnly: true,
                        });
                    }else{
                        NewColumnHeaders.splice(col, 0, {
                            data: ColumnHeaders[col],
                        });
                    }
                }
                $GridBookContainer.handsontable({
                    data: data,
                    colHeaders: ColumnHeaders,
                    columns: NewColumnHeaders,
                    contextMenu: false,
                    disableVisualSelection: true,
                    renderAllRows: true,
                    rowHeaders: true,
                    nestedRows: true,
                    autoColumnSize : true,
                    licenseKey: 'non-commercial-and-evaluation',
                    className: "htCenter",
                    beforeChange: function(changes, source) {
                        var updatedData = {};
                        var rowIndex = changes[0][0];
                        var searchArr = ["Semester","Quarter","Subject","Name"];
                        var data = this.getSourceData();
                        if(data[rowIndex].hasOwnProperty("Name")){
                            searchArr = ["Semester","Quarter","Subject","Name"];
                        }else if(data[rowIndex].hasOwnProperty("Subject")){
                            searchArr = ["Semester","Quarter","Subject"];
                        }else if(data[rowIndex].hasOwnProperty("Quarter")){
                            searchArr = ["Semester","Quarter"];
                        }else if(data[rowIndex].hasOwnProperty("Semester")){
                            searchArr = ["Semester"];
                        }
                        for(var i= searchArr.length -1 ; i >= 0 ; i--){
                            var currentArr = searchArr[i];
                            for(var j= rowIndex; j > 0; j--){
                                var currentData = data[j];
                                if(currentData.hasOwnProperty(currentArr)){
                                    if(currentData[currentArr] != null){
                                        updatedData[currentArr] = currentData[currentArr];
                                        break;
                                    }
                                }
                            }
                            searchArr.splice(searchArr.indexOf(currentArr), 1);
                        }
                        updatedData[changes[0][1]] = changes[0][3];
                        self._rpc({
                            model: "gradebook.gradebook",
                            method: "update_student_override_data",
                            args: [self.student_progression_id,updatedData],
                        }).then(function(data){
                            location.reload();
                        });
                    },
                });
                var hotInstance = $GridBookContainer.handsontable('getInstance');
                setTimeout(function(){ hotInstance.render(); },10);
            }
        },
    });
    core.action_registry.add('grade_book_grade_book_grid', GridGradeBook);

    return GridGradeBook;
});
