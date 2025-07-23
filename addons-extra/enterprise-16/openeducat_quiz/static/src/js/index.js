odoo.define('openeducat_quiz.lms_openeducat_quiz', function (require) {
    'use strict';
    var core = require("web.core");
    var ajax = require("web.ajax");
    var Widget = require("web.Widget");
    var QWeb = core.qweb;
    var publicWidget = require('web.public.widget');
    var _t = core._t;

    publicWidget.registry.lms_openeducat_quiz = publicWidget.Widget.extend({

        events: {
            'click .quiz_nxt': '_quiz_nxt',
            'click .quiz_prv': '_quiz_prv',
            'click .question_grid_btn': '_question_grid_btn',
            'click .quiz_finish': '_quiz_result_attempt',
        },
        selector: '.lms_form-horizontal',

        jsLibs: [
        ],
        xmlDependencies: [
            '/openeducat_quiz/static/src/xml/question.xml'
        ],
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            self._quiz_first_que();

        },
        _getData: function () {
            var self = this;

        },
        _call_question_template: function (res) {
            var self = this;
            // console.log(res,"..prev_que");
            if (res) {
                $('.quiz_nxt').val(parseInt(res.next_que[0].id))
                $('.quiz_prv').val(parseInt(res.next_que[0].id))
                $('#question_template').replaceWith($(QWeb.render('op_quiz_question', { res: res.next_que,
                     quiz: res.quiz,
                     section_name: res.section_name,
                     })));
                if (res.next_que[0].last_que) {
                    $('.quiz_nxt').addClass('d-none');
                    $('.quiz_finish').removeClass('d-none');
                } else {
                    $('.quiz_nxt').removeClass('d-none');
                    $('.quiz_finish').addClass('d-none');
                }
                if(res.question_no == 1){
                    $('.quiz_prv').addClass('d-none');
                }else{
                    $('.quiz_prv').removeClass('d-none');
                }
                core.bus.trigger('question_template_updated')
            }
        },
        que_required() {
            var self = this
            if ($('input[type=radio]:checked').length) {
                return true
            }
            else {
                self.displayNotification({ message: _t('Answer required'), type: 'danger' });
            }

        },
        _quiz_nxt: function () {
            var self = this;
            var result_id = parseInt($('input[name=line_result_id]').val())
            var que_id = parseInt($('.quiz_nxt').val())
            var answer
            if ($('.question[value=' + que_id + ']').attr('type') == 'optional') {
                answer = $('.question[value=' + que_id + ']').find('.answer input:checked').attr('value')
            }
            if ($('.question[value=' + que_id + ']').attr('type') == 'blank') {
                answer = $('.question[value=' + que_id + ']').find('input[name=answer]').val();
            }
            if ($('.question[value=' + que_id + ']').attr('type') == 'descriptive') {
                answer = $('.question[value=' + que_id + ']').find('textarea[id=descriptive_ans]').val();
            }
            if ($('.question[value=' + que_id + ']').attr('type') == 'numeric') {
                answer = $('.question[value=' + que_id + ']').find('input[id=numeric_answer]').val();
            }
            ajax.jsonRpc('/get/quiz-data', 'call',
                {
                    'result_id': result_id,
                    'que_id': que_id,
                    'answer': answer,
                }).then(function (res) {
                    self.que_required = res.quiz.que_required
                    var temp = parseInt($('.question').attr('value'));
                    if ($('input[type=radio]:checked').length || $('#descriptive_ans').val()) {
                        $('.question_grid_btn[value=' + temp + ']').addClass("quiz_req");
                    }
                    else if (res.given_answer) {
                        $('.question_grid_btn[value=' + temp + ']').addClass("quiz_req");
                    }
                    else{
                        $('.question_grid_btn[value=' + temp + ']').removeClass("quiz_req");
                    }
                  self._check_multiple_choice()
                    self._call_question_template(res)
                });

        },
        _check_multiple_choice(){
            $('.question[type="multiple_choice"]').each(function( index ) {
                var question_id = $(this).attr("value")
                $(this).find('.multiple_choice_image_div').each(function( index ) {
                    if($(this).hasClass('active')){
                        $('.question_grid_btn[value= '+ question_id +' ]').addClass("quiz_req");
                    }
                })
                $(this).find('.quiz_multiple_choice_text').each(function( index ) {
                    if($(this).is(':checked')){
                        $('.question_grid_btn[value= '+ question_id +' ]').addClass("quiz_req");
                    }
                });
              });
        },
        _quiz_prv: function () {
            var self = this;
            var result_id = parseInt($('input[name=line_result_id]').val())
            var que_id = parseInt($('.quiz_prv').val())
            var answer
            if ($('.question[value=' + que_id + ']').attr('type') == 'optional') {
                answer = $('.question[value=' + que_id + ']').find('.answer input:checked').attr('value')
            }
            if ($('.question[value=' + que_id + ']').attr('type') == 'blank') {
                answer = $('.question[value=' + que_id + ']').find('input[name=answer]').val();
            }
            if ($('.question[value=' + que_id + ']').attr('type') == 'descriptive') {
                answer = $('.question[value=' + que_id + ']').find('textarea[id=descriptive_ans]').val();
            }
            if ($('.question[value=' + que_id + ']').attr('type') == 'numeric') {
                answer = $('.question[value=' + que_id + ']').find('input[id=numeric_answer]').val();
            }
            ajax.jsonRpc('/get/prev-question-data', 'call',
                {
                    'result_id': result_id,
                    'que_id': que_id,
                    'answer': answer,
                }).then(function (res) {
                    var temp = parseInt($('.question').attr('value'));
                    if ($('input[type=radio]:checked').length || $('#descriptive_ans').val()) {
                        $('.question_grid_btn[value=' + temp + ']').addClass("quiz_req");
                    }
                    else if (answer) {
                        $('.question_grid_btn[value=' + temp + ']').addClass("quiz_req");
                    }
                    else{
                        $('.question_grid_btn[value=' + temp + ']').removeClass("quiz_req");
                    }
                    self._check_multiple_choice();
                    self._call_question_template(res)
                });

        },

        _quiz_first_que: function () {
            var self = this;
            var result_id = parseInt($('input[name=line_result_id]').val())
            var que_id = parseInt($('.quiz_nxt').val())
            ajax.jsonRpc('/get/first_que/quiz-data', 'call',
                {
                    'result_id': result_id,
                    'que_id': que_id,
                }).then(function (res) {
                    if (res.state == "submit") {
                        $('#result_form').submit();
                    }
                    else{
                        self._call_question_template(res)
                    }

                });

        },
        _question_grid_btn: function (e) {
            var self = this;
            var result_id = parseInt($('input[name=line_result_id]').val())
            var que_id = parseInt($(e.currentTarget).attr('value'))
            var current_que = parseInt($('.question').attr('value'))
            var answer
            if ($('.question[value=' + current_que + ']').attr('type') == 'optional') {
                answer = $('.question[value=' + current_que + ']').find('.answer input:checked').attr('value')
            }
            if ($('.question[value=' + current_que + ']').attr('type') == 'blank') {
                answer = $('.question[value=' + current_que + ']').find('input[name=answer]').val();
            }
            if ($('.question[value=' + current_que + ']').attr('type') == 'descriptive') {
                answer = $('.question[value=' + current_que + ']').find('textarea[id=descriptive_ans]').val();
            }
            if ($('.question[value=' + current_que + ']').attr('type') == 'numeric') {
                answer = $('.question[value=' + current_que + ']').find('input[id=numeric_answer]').val();
            }
            ajax.jsonRpc('/get/grid_question_data', 'call',
                {
                    'result_id': result_id,
                    'que_id': que_id,
                    'current_que':current_que,
                    'answer':answer,
                }).then(function (res) {
                    var temp = parseInt($('.question').attr('value'));
                    if ($('input[type=radio]:checked').length || $('#descriptive_ans').val()) {
                        $('.question_grid_btn[value=' + temp + ']').addClass("quiz_req");
                    }
                    else if (answer) {
                        $('.question_grid_btn[value=' + temp + ']').addClass("quiz_req");
                    }
                    else{
                        $('.question_grid_btn[value=' + temp + ']').removeClass("quiz_req");
                    }
                    self._check_multiple_choice()
                    self._call_question_template(res)
                });

        },
        _quiz_result_attempt: async function () {
            var self = this;
            var result_id = parseInt($('input[name=line_result_id]').val())
            var que_req = 0
            var que_id = parseInt($('.quiz_finish').val())
            var current_que = parseInt($('.question').attr('value'))
            if ($('input[type=radio]:checked').length) {
                var temp = parseInt($('.question').attr('value'));
                await $('.question_grid_btn[value=' + temp + ']').addClass("quiz_req");
            }
            self._check_multiple_choice();
            if (self.que_required) {
                $('.question_grid_btn').each(function (e) {
                    var answer = $(this).css('background-color')
                    if (!$(this).hasClass('quiz_req')) {
                        que_req = 1
                    }
                })
            }
            var answer
            if ($('.question[value=' + current_que + ']').attr('type') == 'optional') {
                answer = $('.question[value=' + current_que + ']').find('.answer input:checked').attr('value')
            }
            else if ($('.question[value=' + current_que + ']').attr('type') == 'blank') {
                answer = $('.question[value=' + current_que + ']').find('input[name=answer]').val();
            }
            else if ($('.question[value=' + current_que + ']').attr('type') == 'descriptive') {
                answer = $('.question[value=' + current_que + ']').find('textarea[id=descriptive_ans]').val();
            }
            else if ($('.question[value=' + current_que + ']').attr('type') == 'numeric') {
                answer = $('.question[value=' + current_que + ']').find('input[id=numeric_answer]').val();
            }
            if (que_req == 0) {
                ajax.jsonRpc('/quiz/attempt-record', 'call',
                    {
                        'result_id': result_id,
                        'que_id': current_que,
                        'answer': answer,
                    }).then(function (res) {
                        $('#result_form').submit();
                    });
            } else {
                self.displayNotification({ message: _t('Answer required'), type: 'danger' });
            }

        },
    });
    return publicWidget.registry.lms_openeducat_quiz;
});
