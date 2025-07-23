odoo.define('openeducat_grading.grid_grade_book', function(require) {
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

    var GradeBook = AbstractAction.extend({
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
        },
        init: function(parent, state, params) {
            this._super.apply(this, arguments);
            this.student_progression_id = state.params.grade_book;
        },
        start: function() {
            var self = this;
            this._rpc({
                model: "gradebook.gradebook",
                method: "get_all_student_grade_data",
                args: [this.student_progression_id],
            }).then(function(data){
                for(var d=0; d< data.length; d++){
                    var currentData = data[d];
                    self._renderAssignmentWise(JSON.parse(currentData['data']) ,currentData['credit'], currentData['name']);
                }
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
            this._rpc({
                model: "op.student.progression",
                method: "get_grade_book_grid_data",
                args: [parseInt(currentId)],
            }).then(function(data){
                self.grade_book_data = JSON.parse(data);
                var dropDownValue = self.$el.find("#grid_view_drop_down").val();
                if(dropDownValue == 'semester'){
                    self._renderSemesterTermWise(self.grade_book_data);
                    self._renderCommentTable(self.grade_book_data);
                }else if(dropDownValue == 'term_subject'){
                    self._renderTermSubjectWise(self.grade_book_data);
                    self._renderCommentTable(self.grade_book_data);
                }else if(dropDownValue == 'subject'){
                    self._renderSubjectWise(self.grade_book_data);
                    self._renderCommentTable(self.grade_book_data);
                }else if(dropDownValue == 'assignment'){
                    self._renderAssignmentWise(self.grade_book_data);
                    self._renderCommentTable(self.grade_book_data);
                }else if(dropDownValue == 'npa_transcript'){
                    self._renderNpaTranscript(self.grade_book_data);
                    self._renderCommentTable(self.grade_book_data);
                }
            });
        },
        _renderCommentTable: function(grade_data){
            var grid_data = grade_data;
            this.QuarterTermBool = false;
            var self = this;
            var $CommentContainer = $(QWeb.render('grade_book_comment_table_template'));
            this.$CommentContainer = $CommentContainer;
            this.$el.find('.o_content').append($CommentContainer);
            var lastHeaders = [];
            var lastData = [];
            var lastDataDict = {};
            var commentData = [];
            $CommentContainer.wrap('<div class="new-parent p-3"></div>');
            var data = [];
            var dataLength = Object.keys(grid_data).length;
            var objectData = Object.keys(grid_data);
            var ColumnHeaders = ["Year","Semester","Quarter","Total"];
            var yearData = {};
            yearData['__children'] = [];
            for(var i=0; i< dataLength; i++){
                //yearData['Year'] = objectData[i];
                var yearDataLength = Object.keys(grid_data[objectData[i]]).length;
                var yearDataKeys = Object.keys(grid_data[objectData[i]]);
                var yearDataData = grid_data[objectData[i]];
                //----Check Quarter---
                for(var k=0;k < yearDataKeys.length; k++){
                    var currentNode =  yearDataKeys[k];
                    if(currentNode.includes("Quarter")){
                        this.QuarterTermBool = true;
                        break;
                    }
                }
                if(objectData[i].includes('Year') == false){
                    var semesterData = {};
                    semesterData['Semester'] = objectData[i];
                    if(yearDataData.hasOwnProperty('Total')){
                        lastHeaders.push(objectData[i]);
                        lastDataDict[objectData[i]] = yearDataData.Total;
                    }
                    if(yearDataData.hasOwnProperty('Comment')){
                        commentData.push({
                            "Subject" : null,
                            "Term" : objectData[i],
                            "Comment" : yearDataData.Comment,
                        });
                    }
                    semesterData['__children'] = [];
                    //var semesterSubData = {};
                    if(!this.QuarterTermBool){
                        if(ColumnHeaders.includes('Quarter')){
                            var inx = ColumnHeaders.indexOf('Quarter');
                            ColumnHeaders.splice(inx,1);
                        }
                        for(var j=0; j < yearDataLength; j++){
                            if(typeof(yearDataData[yearDataKeys[j]]) == 'object'){
                                if(yearDataData[yearDataKeys[j]].hasOwnProperty('Comment')){
                                    commentData.push({
                                        "Subject" : yearDataKeys[j],
                                        "Term" : objectData[i],
                                        "Comment" : yearDataData[yearDataKeys[j]].Comment,
                                    });
                                }else{
                                    semesterData[yearDataKeys[j]] = yearDataData[yearDataKeys[j]].Mark;
                                }
                            }else{
                                if(yearDataKeys[j] != "Comment"){
                                    semesterData[yearDataKeys[j]] = yearDataData[yearDataKeys[j]];
                                }
                            }
                            if(yearDataKeys[j] != "Comment"){
                                ColumnHeaders.push(yearDataKeys[j]);
                            }
                            //semesterSubData[yearDataKeys[j]] = yearDataData[yearDataKeys[j]];
                        }
                        //semesterData['__children'].push(semesterSubData);
                        yearData['__children'].push(semesterData);
                    }else{
                        for(var l=0; l < yearDataLength; l++){
                            var quarterData = {};
                            if(typeof(yearDataData[yearDataKeys[l]]) == 'object'){
                                var QuarterDataLength = Object.keys(yearDataData[yearDataKeys[l]]).length;
                                var QuarterDataKeys = Object.keys(yearDataData[yearDataKeys[l]]);
                                var QuarterDataData = yearDataData[yearDataKeys[l]];
                                quarterData['Quarter'] = yearDataKeys[l];
                                if(QuarterDataData.hasOwnProperty('Total')){
                                    lastHeaders.push(yearDataKeys[l]);
                                    lastDataDict[yearDataKeys[l]] = QuarterDataData.Total;
                                }
                                quarterData['Total'] = null;
                                quarterData['__children'] = [];
                                //var subQuarterData = {};
                                for(var x=0; x < QuarterDataLength;x++){
                                    if(typeof(QuarterDataData[QuarterDataKeys[x]]) == 'object'){
                                        if(QuarterDataData[QuarterDataKeys[x]].hasOwnProperty('Comment')){
                                            commentData.push({
                                                "Subject" : QuarterDataKeys[x],
                                                "Term" : yearDataKeys[l],
                                                "Comment" : QuarterDataData[QuarterDataKeys[x]].Comment,
                                            })
                                        }else{
                                            quarterData[QuarterDataKeys[x]] = QuarterDataData[QuarterDataKeys[x]].Mark;
                                        }
                                    }else{
                                        if(QuarterDataKeys[x] !== "Comment"){
                                            quarterData[QuarterDataKeys[x]] = QuarterDataData[QuarterDataKeys[x]];
                                        }else{
                                            commentData.push({
                                                "Subject": null,
                                                "Term" : yearDataKeys[l],
                                                "Comment" : QuarterDataData[QuarterDataKeys[x]],
                                            })
                                        }
                                    }
                                    //semesterData[QuarterDataKeys[x]] = null;
                                    if(yearDataKeys[l] != "Comment"){
                                        ColumnHeaders.push(QuarterDataKeys[x]);
                                    }
                                }
                                //quarterData['__children'].push(subQuarterData);
                            }else{
                                if(yearDataKeys[l] != "Comment"){
                                    semesterData['Total'] = yearDataData[yearDataKeys[l]];
                                    //semesterData[childrenDataKeys[j]] = null;
                                    ColumnHeaders.push(yearDataKeys[l]);
                                }
                            }
                            if(Object.keys(quarterData).length !== 0){
                                //quarterArray.push(quarterData);
                                semesterData['__children'].push(quarterData);
                            }
                        }
                        yearData['__children'].push(semesterData);
                    }
                }else{
                    if(this.QuarterTermBool){
                        yearData['Year'] = objectData[i];
                        yearData['Semester'] = null;
                        yearData['Quarter'] = null;
                        yearData['Total'] = yearDataData;
                        lastHeaders.push(objectData[i]);
                        lastDataDict[objectData[i]] = yearDataData;
                    }else{
                        yearData['Year'] = objectData[i];
                        yearData['Semester'] = null;
                        yearData['Total'] = yearDataData;
                        lastHeaders.push(objectData[i]);
                        lastDataDict[objectData[i]] = yearDataData;
                    }
                }
            }
            data.push(yearData);
            for(var s=0;s < data.length; s++){
                var tempSemData = data[s];
                var tempSemDataKeys = Object.keys(data[s]);
                var tempSemDataLength = Object.keys(data[s]).length;
                for(var l=0; l < ColumnHeaders.length; l++){
                    if(tempSemDataKeys.includes(ColumnHeaders[l]) == false && ColumnHeaders[l] != '__children'){
                        if(ColumnHeaders[l] != "Comment"){
                            tempSemData[ColumnHeaders[l]] = null;
                        }
                    }
                }
            }
            ColumnHeaders = ColumnHeaders.filter( function( item, index, inputArray ) {
                   return inputArray.indexOf(item) == index;
            });
            if(this.QuarterTermBool){
                if(ColumnHeaders.includes('Comment')){
                    ColumnHeaders.splice(ColumnHeaders.indexOf('Comment'), 1);
                }
            }
            var CommentHeaders = ["Subject","Term","Comment"]
            lastData.push(lastDataDict);
            var deleteHeaders = ["Year","Semester","Quarter","Total"];
            var rowHeaders = [...ColumnHeaders];
            for(var f=rowHeaders.length - 1; f >= 0; f--){
                if(rowHeaders[f] == "Year" || rowHeaders[f] == "Semester" || rowHeaders[f] == "Quarter" || rowHeaders[f] == "Total" || rowHeaders[f] == "GPA"){
                    rowHeaders.splice(f , 1);
                }
            }
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
        _renderSemesterTermWise: function(grade_data){
            var grid_data = grade_data;
            this.QuarterTermBool = false;
            this.creditAvailable = false;
            var self = this;
            var $GridBookContainer = $(QWeb.render('grade_book_widget_template'));
            this.$GridBookContainer = $GridBookContainer;
            this.$el.find('.o_content').append($GridBookContainer);
            var lastHeaders = [];
            var lastData = [];
            var lastDataDict = {};
            $GridBookContainer.wrap('<div class="new-parent p-3"></div>');
            var data = [];
            var dataLength = Object.keys(grid_data).length;
            var objectData = Object.keys(grid_data);
            var ColumnHeaders = ["Year","Semester","Quarter","Total"];
            var yearData = {};
            yearData['__children'] = [];
            for(var i=0; i< dataLength; i++){
                //yearData['Year'] = objectData[i];
                var yearDataLength = Object.keys(grid_data[objectData[i]]).length;
                var yearDataKeys = Object.keys(grid_data[objectData[i]]);
                var yearDataData = grid_data[objectData[i]];
                //----Check Quarter---
                for(var k=0;k < yearDataKeys.length; k++){
                    var currentNode =  yearDataKeys[k];
                    if(currentNode.includes("Quarter")){
                        this.QuarterTermBool = true;
                        break;
                    }
                }
                if(objectData[i].includes('Year') == false){
                    var semesterData = {};
                    semesterData['Semester'] = objectData[i];
                    if(yearDataData.hasOwnProperty('Total')){
                        lastHeaders.push(objectData[i]);
                        lastDataDict[objectData[i]] = yearDataData.Total;
                    }
                    semesterData['__children'] = [];
                    //var semesterSubData = {};
                    if(!this.QuarterTermBool){
                        if(ColumnHeaders.includes('Quarter')){
                            var inx = ColumnHeaders.indexOf('Quarter');
                            ColumnHeaders.splice(inx,1);
                        }
                        for(var j=0; j < yearDataLength; j++){
                            if(typeof(yearDataData[yearDataKeys[j]]) == 'object'){
                                if(yearDataData[yearDataKeys[j]].hasOwnProperty('Credit')){
                                    this.creditAvailable = true;
                                    semesterData[yearDataKeys[j]] = {
                                        "Grade" : yearDataData[yearDataKeys[j]].Grade,
                                        "Mark" : yearDataData[yearDataKeys[j]].Mark,
                                        "Credit" : yearDataData[yearDataKeys[j]].Credit,
                                    };
                                }else{
                                    semesterData[yearDataKeys[j]] = yearDataData[yearDataKeys[j]].Mark;
                                }
                            }else{
                                semesterData[yearDataKeys[j]] = yearDataData[yearDataKeys[j]];
                            }
                            ColumnHeaders.push(yearDataKeys[j]);
                            //semesterSubData[yearDataKeys[j]] = yearDataData[yearDataKeys[j]];
                        }
                        //semesterData['__children'].push(semesterSubData);
                        yearData['__children'].push(semesterData);
                    }else{
                        for(var l=0; l < yearDataLength; l++){
                            var quarterData = {};
                            if(typeof(yearDataData[yearDataKeys[l]]) == 'object'){
                                var QuarterDataLength = Object.keys(yearDataData[yearDataKeys[l]]).length;
                                var QuarterDataKeys = Object.keys(yearDataData[yearDataKeys[l]]);
                                var QuarterDataData = yearDataData[yearDataKeys[l]];
                                quarterData['Quarter'] = yearDataKeys[l];
                                if(QuarterDataData.hasOwnProperty('Total')){
                                    lastHeaders.push(yearDataKeys[l]);
                                    lastDataDict[yearDataKeys[l]] = QuarterDataData.Total;
                                }
                                quarterData['Total'] = null;
                                quarterData['__children'] = [];
                                //var subQuarterData = {};
                                for(var x=0; x < QuarterDataLength;x++){
                                    if(typeof(QuarterDataData[QuarterDataKeys[x]]) == 'object'){
                                        if(QuarterDataData[QuarterDataKeys[x]].hasOwnProperty('Credit')){
                                            this.creditAvailable = true;
                                            quarterData[QuarterDataKeys[x]] = {
                                                "Grade" : QuarterDataData[QuarterDataKeys[x]].Grade,
                                                "Mark" : QuarterDataData[QuarterDataKeys[x]].Mark,
                                                "Credit" : QuarterDataData[QuarterDataKeys[x]].Credit,
                                            };
                                        }else{
                                            quarterData[QuarterDataKeys[x]] = QuarterDataData[QuarterDataKeys[x]].Mark;
                                        }
                                    }else{
                                        quarterData[QuarterDataKeys[x]] = QuarterDataData[QuarterDataKeys[x]];
                                    }
                                    //semesterData[QuarterDataKeys[x]] = null;
                                    ColumnHeaders.push(QuarterDataKeys[x]);
                                }
                                //quarterData['__children'].push(subQuarterData);
                            }else{
                                semesterData['Total'] = yearDataData[yearDataKeys[l]];
                                //semesterData[childrenDataKeys[j]] = null;
                                ColumnHeaders.push(yearDataKeys[l]);
                            }
                            if(Object.keys(quarterData).length !== 0){
                                //quarterArray.push(quarterData);
                                semesterData['__children'].push(quarterData);
                            }
                        }
                        yearData['__children'].push(semesterData);
                    }
                }else{
                    if(this.QuarterTermBool){
                        yearData['Year'] = objectData[i];
                        yearData['Semester'] = null;
                        yearData['Quarter'] = null;
                        yearData['Total'] = yearDataData;
                        lastHeaders.push(objectData[i]);
                        lastDataDict[objectData[i]] = yearDataData;
                    }else{
                        yearData['Year'] = objectData[i];
                        yearData['Semester'] = null;
                        yearData['Total'] = yearDataData;
                        lastHeaders.push(objectData[i]);
                        lastDataDict[objectData[i]] = yearDataData;
                    }
                }
            }
            data.push(yearData);
            for(var s=0;s < data.length; s++){
                var tempSemData = data[s];
                var tempSemDataKeys = Object.keys(data[s]);
                var tempSemDataLength = Object.keys(data[s]).length;
                for(var l=0; l < ColumnHeaders.length; l++){
                    if(tempSemDataKeys.includes(ColumnHeaders[l]) == false && ColumnHeaders[l] != '__children'){
                        tempSemData[ColumnHeaders[l]] = null;
                    }
                }
            }
            ColumnHeaders = ColumnHeaders.filter( function( item, index, inputArray ) {
                   return inputArray.indexOf(item) == index;
            });
            lastData.push(lastDataDict);
            var deleteHeaders = ["Year","Semester","Quarter","Total"];
            var rowHeaders = [...ColumnHeaders];
            for(var f=rowHeaders.length - 1; f >= 0; f--){
                if(rowHeaders[f] == "Year" || rowHeaders[f] == "Semester" || rowHeaders[f] == "Quarter" || rowHeaders[f] == "Total" || rowHeaders[f] == "GPA"){
                    rowHeaders.splice(f , 1);
                }
            }
            $GridBookContainer.handsontable({
                data: lastData,
                colHeaders: lastHeaders,
                contextMenu: false,
                editor: false,
                disableVisualSelection: true,
                nestedRows: true,
                rowHeaders: true,
                licenseKey: 'non-commercial-and-evaluation',
                className: "htCenter",
            });
            var hotInstance = $GridBookContainer.handsontable('getInstance');
            setTimeout(function(){ hotInstance.render(); },10);
        },
        _renderTermSubjectWise: function(grade_data){
            var grid_data = grade_data;
            var self = this;
            this.QuarterTermBool = false;
            this.creditAvailable = false;
            var $GridBookContainer = $(QWeb.render('grade_book_widget_template'));
            this.$GridBookContainer = $GridBookContainer;
            this.$el.find('.o_content').append($GridBookContainer);
            var lastHeaders = [];
            var lastData = [];
            var lastDataDict = {};
            $GridBookContainer.wrap('<div class="new-parent p-3"></div>');
            var data = [];
            var dataLength = Object.keys(grid_data).length;
            var objectData = Object.keys(grid_data);
            var ColumnHeaders = ["Year","Semester","Quarter","Total"];
            var yearData = {};
            yearData['__children'] = [];
            for(var i=0; i< dataLength; i++){
                //yearData['Year'] = objectData[i];
                var yearDataLength = Object.keys(grid_data[objectData[i]]).length;
                var yearDataKeys = Object.keys(grid_data[objectData[i]]);
                var yearDataData = grid_data[objectData[i]];
                //----Check Quarter---
                for(var k=0;k < yearDataKeys.length; k++){
                    var currentNode =  yearDataKeys[k];
                    if(currentNode.includes("Quarter")){
                        this.QuarterTermBool = true;
                        break;
                    }
                }
                if(objectData[i].includes('Year') == false){
                    var semesterData = {};
                    semesterData['Semester'] = objectData[i];
                    if(yearDataData.hasOwnProperty('Total')){
                        lastHeaders.push(objectData[i]);
                        lastDataDict[objectData[i]] = yearDataData.Total;
                    }
                    semesterData['__children'] = [];
                    //var semesterSubData = {};
                    if(!this.QuarterTermBool){
                        if(ColumnHeaders.includes('Quarter')){
                            var inx = ColumnHeaders.indexOf('Quarter');
                            ColumnHeaders.splice(inx,1);
                        }
                        for(var j=0; j < yearDataLength; j++){
                            if(typeof(yearDataData[yearDataKeys[j]]) == 'object'){
                                if(yearDataData[yearDataKeys[j]].hasOwnProperty('Credit')){
                                    this.creditAvailable = true;
                                    semesterData[yearDataKeys[j]] = {
                                        "Grade" : yearDataData[yearDataKeys[j]].Grade,
                                        "Mark" : yearDataData[yearDataKeys[j]].Mark,
                                        "Credit" : yearDataData[yearDataKeys[j]].Credit,
                                    };
                                }else{
                                    semesterData[yearDataKeys[j]] = yearDataData[yearDataKeys[j]].Mark;
                                }
                            }else{
                                if(yearDataKeys[j] != "Comment"){
                                    semesterData[yearDataKeys[j]] = yearDataData[yearDataKeys[j]];
                                }
                            }
                            if(yearDataKeys[j] != "Comment"){
                                ColumnHeaders.push(yearDataKeys[j]);
                            }
                            //semesterSubData[yearDataKeys[j]] = yearDataData[yearDataKeys[j]];
                        }
                        //semesterData['__children'].push(semesterSubData);
                        yearData['__children'].push(semesterData);
                    }else{
                        for(var l=0; l < yearDataLength; l++){
                            var quarterData = {};
                            if(typeof(yearDataData[yearDataKeys[l]]) == 'object'){
                                var QuarterDataLength = Object.keys(yearDataData[yearDataKeys[l]]).length;
                                var QuarterDataKeys = Object.keys(yearDataData[yearDataKeys[l]]);
                                var QuarterDataData = yearDataData[yearDataKeys[l]];
                                quarterData['Quarter'] = yearDataKeys[l];
                                if(QuarterDataData.hasOwnProperty('Total')){
                                    lastHeaders.push(yearDataKeys[l]);
                                    lastDataDict[yearDataKeys[l]] = QuarterDataData.Total;
                                }
                                quarterData['Total'] = null;
                                quarterData['__children'] = [];
                                //var subQuarterData = {};
                                for(var x=0; x < QuarterDataLength;x++){
                                    if(typeof(QuarterDataData[QuarterDataKeys[x]]) == 'object'){
                                        if(QuarterDataData[QuarterDataKeys[x]].hasOwnProperty('Credit')){
                                            this.creditAvailable = true;
                                            quarterData[QuarterDataKeys[x]] = {
                                                "Grade" : QuarterDataData[QuarterDataKeys[x]].Grade,
                                                "Mark" : QuarterDataData[QuarterDataKeys[x]].Mark,
                                                "Credit" : QuarterDataData[QuarterDataKeys[x]].Credit,
                                            };
                                        }else{
                                            quarterData[QuarterDataKeys[x]] = QuarterDataData[QuarterDataKeys[x]].Mark;
                                        }
                                    }else{
                                        if(QuarterDataKeys[x] !== "Comment"){
                                            quarterData[QuarterDataKeys[x]] = QuarterDataData[QuarterDataKeys[x]];
                                        }
                                    }
                                    //semesterData[QuarterDataKeys[x]] = null;
                                    if(yearDataKeys[l] != "Comment"){
                                        ColumnHeaders.push(QuarterDataKeys[x]);
                                    }
                                }
                                //quarterData['__children'].push(subQuarterData);
                            }else{
                                if(yearDataKeys[l] != "Comment"){
                                    semesterData['Total'] = yearDataData[yearDataKeys[l]];
                                    //semesterData[childrenDataKeys[j]] = null;
                                    ColumnHeaders.push(yearDataKeys[l]);
                                }
                            }
                            if(Object.keys(quarterData).length !== 0){
                                //quarterArray.push(quarterData);
                                semesterData['__children'].push(quarterData);
                            }
                        }
                        yearData['__children'].push(semesterData);
                    }
                }else{
                    if(this.QuarterTermBool){
                        yearData['Year'] = objectData[i];
                        yearData['Semester'] = null;
                        yearData['Quarter'] = null;
                        yearData['Total'] = yearDataData;
                        lastHeaders.push(objectData[i]);
                        lastDataDict[objectData[i]] = yearDataData;
                    }else{
                        yearData['Year'] = objectData[i];
                        yearData['Semester'] = null;
                        yearData['Total'] = yearDataData;
                        lastHeaders.push(objectData[i]);
                        lastDataDict[objectData[i]] = yearDataData;
                    }
                }
            }
            data.push(yearData);
            for(var s=0;s < data.length; s++){
                var tempSemData = data[s];
                var tempSemDataKeys = Object.keys(data[s]);
                var tempSemDataLength = Object.keys(data[s]).length;
                for(var l=0; l < ColumnHeaders.length; l++){
                    if(tempSemDataKeys.includes(ColumnHeaders[l]) == false && ColumnHeaders[l] != '__children'){
                        if(ColumnHeaders[l] != "Comment"){
                            tempSemData[ColumnHeaders[l]] = null;
                        }
                    }
                }
            }
            ColumnHeaders = ColumnHeaders.filter( function( item, index, inputArray ) {
                   return inputArray.indexOf(item) == index;
            });
            if(this.QuarterTermBool){
                if(ColumnHeaders.includes('Comment')){
                    ColumnHeaders.splice(ColumnHeaders.indexOf('Comment'), 1);
                }
            }
            lastData.push(lastDataDict);
            var deleteHeaders = ["Year","Semester","Quarter","Total"];
            var rowHeaders = [...ColumnHeaders];
            for(var f=rowHeaders.length - 1; f >= 0; f--){
                if(rowHeaders[f] == "Year" || rowHeaders[f] == "Semester" || rowHeaders[f] == "Quarter" || rowHeaders[f] == "Total" || rowHeaders[f] == "GPA"){
                    rowHeaders.splice(f , 1);
                }
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
                this.movePlugin = hotInstance.getPlugin('manualColumnMove');
                var moveHeaders = hotInstance.getColHeader();
                if(moveHeaders.includes('GPA')){
                    moveHeaders = hotInstance.getColHeader();
                    this.movePlugin.moveColumn(moveHeaders.indexOf('GPA'), moveHeaders.length - 1);
                }
                if(moveHeaders.includes('Grade')){
                    moveHeaders = hotInstance.getColHeader();
                    this.movePlugin.moveColumn(moveHeaders.indexOf('Grade'), moveHeaders.length - 1);
                }
                if(moveHeaders.includes('Total')){
                    moveHeaders = hotInstance.getColHeader();
                    this.movePlugin.moveColumn(moveHeaders.indexOf('Total'), moveHeaders.length - 1);
                }
                moveHeaders = hotInstance.getColHeader();
                if(this.creditAvailable){
                    var level2Header = [];
                    for(var p=0; p < moveHeaders.length; p++){
                        if(moveHeaders[p] != 'Total' && moveHeaders[p] != 'Semester' && moveHeaders[p] != 'Quarter' && moveHeaders[p] != 'Year' && moveHeaders[p] != 'GPA' && moveHeaders[p] != 'Grade'){
                            moveHeaders[p] = {
                                'label': moveHeaders[p] ,
                                'colspan': 3,
                            }
                            level2Header.push('Mark','Grade','Credit');
                        }else{
                            level2Header.push('');
                        }
                    }
                    var allHeaders = [];
                    allHeaders.push(moveHeaders);
                    allHeaders.push(level2Header);
                    var widthList = [80,80];
                    for(var h=0; h< level2Header.length - 2; h++){
                        widthList.push(65);
                    }
                    hotInstance.updateSettings({
                        nestedHeaders: allHeaders,
                        colWidths: widthList,
                    });
                    var hotInstanceData = hotInstance.getData();
                    if(this.QuarterTermBool){
                        var objectingStart = 2;
                    }else{
                        var objectingStart = 1;
                    }
                    for(var m = objectingStart; m < hotInstanceData.length - 1; m++){
                        var firstList = hotInstanceData[m];
                        var secondList = hotInstanceData[m + 1];
                        for(var n=0;n < firstList.length; n++){
                            if(typeof(firstList[n]) == 'object' && firstList[n] != null){
                                if(secondList[n] == null){
                                    secondList.splice(n , 0 , {
                                        'Mark': '',
                                        'Grade': '',
                                        'Credit': '',
                                    });
                                    secondList.splice(n+1, 1);
                                }
                            }
                        }
                    }
                    for(var q = hotInstanceData.length - 1; q > hotInstanceData.length - objectingStart - 1; q--){
                        var firstList = hotInstanceData[q];
                        var secondList = hotInstanceData[q - 1];
                        for(var w=0;w > firstList.length; w--){
                            if(typeof(firstList[w]) == 'object' && firstList[w] != null){
                                if(secondList[w] == null){
                                    secondList.splice(w , 0 , {
                                        'Mark': '',
                                        'Grade': '',
                                        'Credit': '',
                                    });
                                    secondList.splice(w+1, 1);
                                }
                            }
                        }
                    }
                    var headerLoopVal = 0;
                    for(var c=0; c < hotInstanceData.length; c++){
                        var subHotInstanceData = hotInstanceData[c];
                        for(var d=0;d < subHotInstanceData.length; d++){
                            if(typeof(subHotInstanceData[d]) == 'object' && subHotInstanceData[d] != null){
                                var subData = subHotInstanceData[d];
                                hotInstanceData[c].splice( d , 0 , subData.Mark);
                                hotInstanceData[c].splice( d+1 , 0 , subData.Grade);
                                hotInstanceData[c].splice( d+2 , 0 , subData.Credit);
                                hotInstanceData[c].splice( d+3 ,1);
                                if(hotInstanceData[c].length > headerLoopVal){
                                    headerLoopVal = hotInstanceData[c].length;
                                }
                            }
                        }
                    }
                    hotInstanceData.forEach(function(value,key){
                        var len = headerLoopVal - value.length;
                        if(len !== 0){
                            for(var w=0; w < len; w++){
                                if(self.QuarterTermBool){
                                    hotInstanceData[key].splice(hotInstanceData[key].length - 2,0,null);
                                }else{
                                    hotInstanceData[key].splice(hotInstanceData[key].length - 3,0,null);
                                }
                            }
                        }
                    });
                    hotInstance.loadData(hotInstanceData);
                }
            setTimeout(function(){ hotInstance.render(); },10);
        },
        _renderSubjectWise: function(grade_data){
            var grid_data = grade_data;
            this.QuarterTermBool = false;
            this.creditAvailable = false;
            var self = this;
            var $GridBookContainer = $(QWeb.render('grade_book_widget_template'));
            this.$GridBookContainer = $GridBookContainer;
            this.$el.find('.o_content').append($GridBookContainer);
            var lastHeaders = [];
            var lastData = [];
            var lastDataDict = {};
            $GridBookContainer.wrap('<div class="new-parent p-3"></div>');
            var data = [];
            var quarterSubject = {};
            var dataLength = Object.keys(grid_data).length;
            var objectData = Object.keys(grid_data);
            var ColumnHeaders = ["Year","Semester","Quarter","Total"];
            var yearData = {};
            yearData['__children'] = [];
            for(var i=0; i< dataLength; i++){
                //yearData['Year'] = objectData[i];
                var yearDataLength = Object.keys(grid_data[objectData[i]]).length;
                var yearDataKeys = Object.keys(grid_data[objectData[i]]);
                var yearDataData = grid_data[objectData[i]];
                //----Check Quarter---
                for(var k=0;k < yearDataKeys.length; k++){
                    var currentNode =  yearDataKeys[k];
                    if(currentNode.includes("Quarter")){
                        this.QuarterTermBool = true;
                        break;
                    }
                }
                if(objectData[i].includes('Year') == false){
                    var semesterData = {};
                    semesterData['Semester'] = objectData[i];
                    if(yearDataData.hasOwnProperty('Total')){
                        lastHeaders.push(objectData[i]);
                        lastDataDict[objectData[i]] = yearDataData.Total;
                    }
                    semesterData['__children'] = [];
                    //var semesterSubData = {};
                    if(!this.QuarterTermBool){
                        if(ColumnHeaders.includes('Quarter')){
                            var inx = ColumnHeaders.indexOf('Quarter');
                            ColumnHeaders.splice(inx,1);
                        }
                        for(var j=0; j < yearDataLength; j++){
                            if(typeof(yearDataData[yearDataKeys[j]]) == 'object'){
                                if(yearDataData[yearDataKeys[j]].hasOwnProperty('Credit')){
                                    this.creditAvailable = true;
                                    quarterSubject[yearDataKeys[j] + " " + objectData[i]] = yearDataData[yearDataKeys[j]].Mark;
                                    quarterSubject[yearDataKeys[j] + " " + objectData[i]] = {
                                        "Mark" : yearDataData[yearDataKeys[j]].Mark,
                                        "Credit" : yearDataData[yearDataKeys[j]].Credit,
                                        "Name" : yearDataKeys[j],
                                    };
                                    semesterData[yearDataKeys[j]] = {
                                        "Grade" : yearDataData[yearDataKeys[j]].Grade,
                                        "Mark" : yearDataData[yearDataKeys[j]].Mark,
                                        "Credit" : yearDataData[yearDataKeys[j]].Credit,
                                    };
                                }else{
                                    quarterSubject[yearDataKeys[j] + " " + objectData[i]] = yearDataData[yearDataKeys[j]].Mark;
                                    semesterData[yearDataKeys[j]] = yearDataData[yearDataKeys[j]].Mark;
                                }
                            }else{
                                if(yearDataKeys[j] != "Comment"){
                                    quarterSubject[yearDataKeys[j] + " " + objectData[i]] = yearDataData[yearDataKeys[j]];
                                    semesterData[yearDataKeys[j]] = yearDataData[yearDataKeys[j]];
                                }
                            }
                            ColumnHeaders.push(yearDataKeys[j]);
                            //semesterSubData[yearDataKeys[j]] = yearDataData[yearDataKeys[j]];
                        }
                        //semesterData['__children'].push(semesterSubData);
                        yearData['__children'].push(semesterData);
                    }else{
                        for(var l=0; l < yearDataLength; l++){
                            var quarterData = {};
                            if(typeof(yearDataData[yearDataKeys[l]]) == 'object'){
                                var QuarterDataLength = Object.keys(yearDataData[yearDataKeys[l]]).length;
                                var QuarterDataKeys = Object.keys(yearDataData[yearDataKeys[l]]);
                                var QuarterDataData = yearDataData[yearDataKeys[l]];
                                quarterData['Quarter'] = yearDataKeys[l];
                                lastHeaders.push(yearDataKeys[l]);
                                lastDataDict[yearDataKeys[l]] = QuarterDataData.Total;
                                quarterData['Total'] = null;
                                quarterData['__children'] = [];
                                //var subQuarterData = {};
                                for(var x=0; x < QuarterDataLength;x++){
                                    if(typeof(QuarterDataData[QuarterDataKeys[x]]) == 'object'){
                                        if(QuarterDataData[QuarterDataKeys[x]].hasOwnProperty('Credit')){
                                            this.creditAvailable = true;
                                            quarterSubject[QuarterDataKeys[x] + " " + yearDataKeys[l]] = {
                                                "Mark" : QuarterDataData[QuarterDataKeys[x]].Mark,
                                                "Credit" : QuarterDataData[QuarterDataKeys[x]].Credit,
                                                "Name" : QuarterDataKeys[x],
                                            };
                                            quarterData[QuarterDataKeys[x]] = {
                                                "Grade" : QuarterDataData[QuarterDataKeys[x]].Grade,
                                                "Mark" : QuarterDataData[QuarterDataKeys[x]].Mark,
                                                "Credit" : QuarterDataData[QuarterDataKeys[x]].Credit,
                                            };
                                        }else{
                                            quarterSubject[QuarterDataKeys[x] + " " + yearDataKeys[l]] = QuarterDataData[QuarterDataKeys[x]].Mark;
                                            quarterData[QuarterDataKeys[x]] = QuarterDataData[QuarterDataKeys[x]].Mark;
                                        }
                                    }else{
                                        if(QuarterDataKeys[x] != "Comment"){
                                            quarterSubject[QuarterDataKeys[x] + " " + yearDataKeys[l]] = QuarterDataData[QuarterDataKeys[x]];
                                            quarterData[QuarterDataKeys[x]] = QuarterDataData[QuarterDataKeys[x]];
                                        }
                                    }
                                    //semesterData[QuarterDataKeys[x]] = null;
                                    if(QuarterDataKeys[x] != "Comment"){
                                        ColumnHeaders.push(QuarterDataKeys[x]);
                                    }
                                }
                                //quarterData['__children'].push(subQuarterData);
                            }else{
                                if(yearDataKeys[l] != "Comment"){
                                    semesterData['Total'] = yearDataData[yearDataKeys[l]];
                                    //semesterData[childrenDataKeys[j]] = null;
                                    ColumnHeaders.push(yearDataKeys[l]);
                                }
                            }
                            if(Object.keys(quarterData).length !== 0){
                                //quarterArray.push(quarterData);
                                semesterData['__children'].push(quarterData);
                            }
                        }
                        yearData['__children'].push(semesterData);
                    }
                }else{
                    if(this.QuarterTermBool){
                        yearData['Year'] = objectData[i];
                        yearData['Semester'] = null;
                        yearData['Quarter'] = null;
                        yearData['Total'] = yearDataData;
                        lastHeaders.push(objectData[i]);
                        lastDataDict[objectData[i]] = yearDataData;
                    }else{
                        yearData['Year'] = objectData[i];
                        yearData['Semester'] = null;
                        yearData['Total'] = yearDataData;
                        lastHeaders.push(objectData[i]);
                        lastDataDict[objectData[i]] = yearDataData;
                    }
                }
            }
            data.push(yearData);
            for(var s=0;s < data.length; s++){
                var tempSemData = data[s];
                var tempSemDataKeys = Object.keys(data[s]);
                var tempSemDataLength = Object.keys(data[s]).length;
                for(var l=0; l < ColumnHeaders.length; l++){
                    if(tempSemDataKeys.includes(ColumnHeaders[l]) == false && ColumnHeaders[l] != '__children' ){
                        tempSemData[ColumnHeaders[l]] = null;
                    }
                }
            }
            ColumnHeaders = ColumnHeaders.filter( function( item, index, inputArray ) {
                   return inputArray.indexOf(item) == index;
            });
            lastData.push(lastDataDict);
            var deleteHeaders = ["Year","Semester","Quarter","Total"];
            var rowHeaders = [...ColumnHeaders];
            if(this.creditAvailable){
                for(var f=rowHeaders.length - 1; f >= 0; f--){
                    if(rowHeaders[f] == "Year" || rowHeaders[f] == "Semester" || rowHeaders[f] == "Quarter" || rowHeaders[f] == "Comment"){
                        rowHeaders.splice(f , 1);
                    }
                }
            }else{
                for(var f=rowHeaders.length - 1; f >= 0; f--){
                    if(rowHeaders[f] == "Year" || rowHeaders[f] == "Semester" || rowHeaders[f] == "Quarter" || rowHeaders[f] == "Total" || rowHeaders[f] == "Comment"){
                        rowHeaders.splice(f , 1);
                    }
                }
            }
            if(this.QuarterTermBool){
                var finalQuarterData = [];
                for(var v=0; v < lastHeaders.length; v++){
                    if(lastHeaders[v].includes('Semester') || lastHeaders[v].includes('Year')){
                        lastHeaders.splice(v, 1);
                    }
                }
                var quarterSubjectKeys = Object.keys(quarterSubject);
                for(var u=0; u < rowHeaders.length; u++){
                    var finalQuarter = {};
                    for(var h=0; h < lastHeaders.length; h++){
                        for(var t=0; t < quarterSubjectKeys.length; t++){
                            if(quarterSubjectKeys[t].includes(rowHeaders[u]) && quarterSubjectKeys[t].includes(lastHeaders[h])){
                                if(typeof(quarterSubject[quarterSubjectKeys[t]]) == "object" && quarterSubject[quarterSubjectKeys[t]].Name == rowHeaders[u]){
                                    finalQuarter[lastHeaders[h]] = quarterSubject[quarterSubjectKeys[t]];
                                }
                                if(typeof(quarterSubject[quarterSubjectKeys[t]]) != "object"){
                                    finalQuarter[lastHeaders[h]] = quarterSubject[quarterSubjectKeys[t]];
                                }
                            }
                        }
                    }
                    finalQuarterData.push(finalQuarter);
                }
                for(var a=0; a < finalQuarterData.length; a++){
                    var tempFinalQuarter = finalQuarterData[a];
                    for(var w=0; w < lastHeaders.length; w++){
                        if(!tempFinalQuarter.hasOwnProperty(lastHeaders[w])){
                            tempFinalQuarter[lastHeaders[w]] = null;
                        }
                    }
                }
            }else{
                var finalQuarterData = [];
                for(var v=0; v < lastHeaders.length; v++){
                    if(lastHeaders[v].includes('Year')){
                        lastHeaders.splice(v, 1);
                    }
                }
                var quarterSubjectKeys = Object.keys(quarterSubject);
                for(var u=0; u < rowHeaders.length; u++){
                    var finalQuarter = {};
                    for(var h=0; h < lastHeaders.length; h++){
                        for(var t=0; t < quarterSubjectKeys.length; t++){
                            if(quarterSubjectKeys[t].includes(rowHeaders[u]) && quarterSubjectKeys[t].includes(lastHeaders[h])){
                                finalQuarter[lastHeaders[h]] = quarterSubject[quarterSubjectKeys[t]];
                            }
                        }
                    }
                    finalQuarterData.push(finalQuarter);
                }
                for(var a=0; a < finalQuarterData.length; a++){
                    var tempFinalQuarter = finalQuarterData[a];
                    for(var w=0; w < lastHeaders.length; w++){
                        if(!tempFinalQuarter.hasOwnProperty(lastHeaders[w])){
                            tempFinalQuarter[lastHeaders[w]] = null;
                        }
                    }
                }
            }
            $GridBookContainer.handsontable({
                data: finalQuarterData,
                colHeaders: lastHeaders,
                contextMenu: false,
                editor: false,
                disableVisualSelection: true,
                rowHeaders: rowHeaders,
                rowHeaderWidth: 180,
                bindRowsWithHeaders: true,
                licenseKey: 'non-commercial-and-evaluation',
                className: "htCenter",
            });
            var hotInstance = $GridBookContainer.handsontable('getInstance');
                this.moveRowPlugin = hotInstance.getPlugin('ManualRowMove');
                var moveRowHeaders = hotInstance.getRowHeader();
                if(moveRowHeaders.includes('Grade')){
                    moveRowHeaders = hotInstance.getRowHeader();
                    this.moveRowPlugin.moveRow(moveRowHeaders.indexOf('Grade'), moveRowHeaders.length - 1);
                }
                if(moveRowHeaders.includes('GPA')){
                    moveRowHeaders = hotInstance.getRowHeader();
                    this.moveRowPlugin.moveRow(moveRowHeaders.indexOf('GPA'), moveRowHeaders.length - 1);
                }
                if(moveRowHeaders.includes('Total')){
                    moveRowHeaders = hotInstance.getRowHeader();
                    this.moveRowPlugin.moveRow(moveRowHeaders.indexOf('Total'), moveRowHeaders.length - 1);
                }
                moveRowHeaders = hotInstance.getRowHeader();
                hotInstance.updateSettings({
                    rowHeaders: moveRowHeaders,
                });
                moveRowHeaders = hotInstance.getRowHeader();
                var moveHeaders = hotInstance.getColHeader();
                if(this.creditAvailable){
                    var level2Header = [];
                    for(var p=0; p < moveHeaders.length; p++){
                        level2Header.push(moveHeaders[p]);
                        level2Header.push('Credit');
                    }
                    hotInstance.updateSettings({
                        colHeaders: level2Header,
                        bindRowsWithHeaders: true,
                    });
                    var hotInstanceData = hotInstance.getData();
                    if(this.QuarterTermBool){
                        var objectingStart = 2;
                    }else{
                        var objectingStart = 1;
                    }
                    for(var m = 0; m < hotInstanceData.length - objectingStart - 1; m++){
                        var firstList = hotInstanceData[m];
                        var secondList = hotInstanceData[m + 1];
                        for(var n=0;n < firstList.length; n++){
                            if(typeof(firstList[n]) == 'object' && firstList[n] != null){
                                if(secondList[n] == null){
                                    secondList.splice(n , 0 , {
                                        'Mark': '',
                                        'Credit': '',
                                    });
                                    secondList.splice(n+1, 1);
                                }
                            }
                        }
                    }
                    for(var q = hotInstanceData.length - objectingStart - 1; q >= 1; q--){
                        var firstList = hotInstanceData[q];
                        var secondList = hotInstanceData[q - 1];
                        for(var w=0;w < firstList.length; w++){
                            if(typeof(firstList[w]) == 'object' && firstList[w] != null){
                                if(secondList[w] == null){
                                    secondList.splice(w , 0 , {
                                        'Mark': '',
                                        'Credit': '',
                                    });
                                    secondList.splice(w+1, 1);
                                }
                            }
                        }
                    }
                    var headerLoopVal = 0;
                    for(var c=0; c < hotInstanceData.length; c++){
                        var subHotInstanceData = hotInstanceData[c];
                        for(var d=0;d < subHotInstanceData.length; d++){
                            if(typeof(subHotInstanceData[d]) == 'object' && subHotInstanceData[d] != null){
                                var subData = subHotInstanceData[d];
                                hotInstanceData[c].splice( d , 0 , subData.Mark);
                                hotInstanceData[c].splice( d+1 , 0 , subData.Credit);
                                hotInstanceData[c].splice( d+2 ,1);
                                if(hotInstanceData[c].length > headerLoopVal){
                                    headerLoopVal = hotInstanceData[c].length;
                                }
                            }
                        }
                    }
                    var lengthLoop = hotInstanceData[hotInstanceData.length - 1].length;
                    if(this.QuarterTermBool){
                        for(var n= hotInstanceData.length -1; n >= hotInstanceData.length - 2; n--){
                            var addNullLoop = hotInstanceData[n];
                            var addNullIndex = 1;
                            for(var p=0; p < lengthLoop; p++){
                                addNullLoop.splice(addNullIndex, 0, null);
                                addNullIndex = addNullIndex + 2;
                            }
                        }
                    }else{
                        for(var n= hotInstanceData.length -1; n >= hotInstanceData.length - 3; n--){
                            var addNullLoop = hotInstanceData[n];
                            var addNullIndex = 1;
                            for(var p=0; p < lengthLoop; p++){
                                addNullLoop.splice(addNullIndex, 0, null);
                                addNullIndex = addNullIndex + 2;
                            }
                        }
                    }
                    hotInstance.loadData(hotInstanceData);
                }
            setTimeout(function(){ hotInstance.render(); },10);
        },
        _renderAssignmentWise: function(grade_data, creditBool, student_name){
            var grid_data = grade_data;
            var self = this;
            this.QuarterTermBool = false;
            this.creditAvailable = creditBool;
            this.attendanceAvailable = false;
            var $GridBookContainer = $(QWeb.render('grade_book_widget_template'));
            this.$GridBookContainer = $GridBookContainer;
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
                for(var r=0; r <yearDataLength; r++){
                    if(typeof(yearDataData[yearDataKeys[r]]) == 'object' && yearDataKeys[r] != "Grade"){
                        var checkQuarterLength = Object.keys(yearDataData[yearDataKeys[r]]).length;
                        var checkQuarterKeys = Object.keys(yearDataData[yearDataKeys[r]]);
                        var checkQuarterData = yearDataData[yearDataKeys[r]];
                        for(var term = 0; term < checkQuarterLength; term++ ){
                            if(typeof(checkQuarterData[checkQuarterKeys[term]]) == 'object'){
                                var checkQuarter = Object.keys(checkQuarterData[checkQuarterKeys[term]]);
                                for(var z=0;z < checkQuarter.length; z++){
                                    var currentNode =  checkQuarter[z];
                                    if(currentNode.includes("Quarter")){
                                        this.QuarterTermBool = true;
                                        break;
                                    }
                                }
                            }
                        }
                    }
                }
                studentData['__children'] = [];
                for(var j=0; j< yearDataLength; j++){
                    if(this.QuarterTermBool){
                        if(typeof(yearDataData[yearDataKeys[j]]) == 'object'){
                            var finaTermData = {};
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
                                    finaTermData['Name'] = null;
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
                            studentData['Name'] = null;
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
                            studentData['Name'] = null;
                            if(this.creditAvailable){
                                studentData['Grade'] =  null;
                                studentData['Credit'] = null;
                                studentData['GPA'] = null;
                            }
                            studentData['Obtained'] = null;
                            studentData['Final Grades'] = null;
                        }
                        studentData['__children'].push(finaTermData)
                    }else{
                        if(typeof(yearDataData[yearDataKeys[j]]) == 'object'){
                            var finaTermData = {};
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
                                    finaTermData['Name'] = null;
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
                            studentData['Name'] = null;
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
                            studentData['Name'] = null;
                            if(this.creditAvailable){
                                studentData['Grade'] =  null;
                                studentData['Credit'] = null;
                                studentData['GPA'] = null;
                            }
                            studentData['Obtained'] = null;
                            studentData['Final Grades'] = null;
                        }
                        studentData['__children'].push(finaTermData);
                    }

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
    core.action_registry.add('grade_book_grid', GradeBook);

    return GradeBook;
});
