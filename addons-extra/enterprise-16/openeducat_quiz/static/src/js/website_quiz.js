odoo.define('openeducat_quiz.quiz', function (require) {
    "use strict";

    var session = require('web.session');
    var start_quiz = () => {
        var tmp_local_storage = {};
        tmp_local_storage.checked_boxes = {};
        tmp_local_storage.blank = {};
        tmp_local_storage.descriptive = {};
        tmp_local_storage.current_que_id = null;

        var exam_id = $("input[name='config_data']").val();
        if (exam_id !== undefined) {
            session.rpc("/quiz/configuration", { result_id: exam_id })
                .then(function (configure_data) {
                    if (configure_data.single_que) {
                        // enable first question of grid
                        if (configure_data.que_required == 1) {
                            var que_grid = $(".que_grid");
                            que_grid.css({
                                'pointer-events': 'none',
                                'cursor': 'default'
                            });
                            $(que_grid[0]).removeAttr('style');
                        }

                        //Reset quiz data while refresh
                        if (localStorage.getItem("quiz") !== null) {
                            tmp_local_storage = JSON.parse(window.localStorage.getItem("quiz"));
                            if(tmp_local_storage && tmp_local_storage.current_que_id){
                                    change_que(tmp_local_storage.current_que_id)

                            for (var i in tmp_local_storage.checked_boxes) {
                                $('#' + tmp_local_storage.checked_boxes[i]).attr('checked', 'true');
                                var que_id = $("input[name='" + i + "']").parent().attr('index-id')
                                $("div[grid-index-id='" + que_id + "']").addClass('que_answered');

                                if (configure_data.prev_readonly == 1 && $('#' + tmp_local_storage.checked_boxes[i]).length > 0) {
                                    var radios = $("input[name='" + i + "']")
                                    for (var i = 0; i < radios.length; i++) {
                                        radios[i].disabled = true;
                                    }
                                }
                                if (configure_data.que_required == 1) {
                                    $("div[grid-index-id='" + que_id + "']").removeAttr('style');
                                }
                            }
                            for (var i in tmp_local_storage.blank) {
                                $('input[name="' + i + '"]').val(tmp_local_storage.blank[i])
                                $('input[name="' + i + '"]').disabled = true;
                            }
                            for (var i in tmp_local_storage.descriptive) {
                                $('textarea[name="' + i + '"]').val(tmp_local_storage.descriptive[i])
                                $('textarea[name="' + i + '"]').disabled = true;

                            }
                            if (tmp_local_storage.current_que_id !== undefined) {
                                $("div[index-id='" + tmp_local_storage.current_que_id + "']").addClass('que_show');
                                $('.que_grid').removeClass('que_active');
                                $("div[grid-index-id='" + tmp_local_storage.current_que_id + "']").addClass('que_active');
                            }
                        }
                        } else {
                            $("div[index-id='" + 0 + "']").addClass('que_show');
                            $('.que_grid').removeClass('que_active');
                            $("div[grid-index-id='" + 0 + "']").addClass('que_active');
                        }

                        //remove prev button and disable question grid
                        if (configure_data.prev_allow == 1) {
                            var que_grid = $(".que_grid");
                            que_grid.css({
                                'pointer-events': 'none',
                                'cursor': 'default'
                            });
                        } else {
                            $('.quiz_prv').remove();
                        }
                        // $(document).on('click', ".quiz_nxt, .quiz_finish", function (e) {
                        //     exam_id =   parseInt($("input[name='config_data']").val());
                        //     var next_id = $(this).attr('next-id');
                        //     console.log(next_id,exam_id,".....\n\n\n")
                        //     $('.que_card').replaceWith('');
                        // });

                        //go next question and checking all configuration
                        // $(document).on('click', ".quiz_nxt, .quiz_finish", function (e) {
                        //     var index_id = $('.que_show').attr('index-id');
                        //     var radio_grp = $("div[index-id='" + index_id + "']").find("input[type='radio']");
                        //     if (radio_grp.length == 0) {
                        //         radio_grp = $("input[type='radio']");
                        //     }
                        //     var radio_grp_name = $(radio_grp[0]).attr('name');
                        //     var next_id = $(this).attr('next-id');
                        //     if ($('.que_show').attr('index-id')) {
                        //         if (configure_data.question_types[index_id] == "optional") {
                        //             if (configure_data.que_required == 1) {
                        //                 if ($("input[name='" + radio_grp_name + "']:checked").length > 0) {
                        //                     change_que(next_id);
                        //                     tmp_local_storage.checked_boxes[radio_grp_name] = $("input[name='" + radio_grp_name + "']:checked").attr('id');
                        //                 } else {
                        //                     required_error();
                        //                     return false;
                        //                 }
                        //             } else {
                        //                 change_que(next_id);
                        //                 tmp_local_storage.checked_boxes[radio_grp_name] = $("input[name='" + radio_grp_name + "']:checked").attr('id');
                        //             }
                        //         } else if (configure_data.question_types[index_id] == "descriptive") {
                        //             if (configure_data.que_required == 1) {
                        //                 if ($(".question[index-id=" + index_id + "]").find("textarea[type='textarea']").val().length == "") {
                        //                     required_error();
                        //                     return false;
                        //                 }
                        //                 else {
                        //                     change_que(next_id);
                        //                     var descriptive_id = $("div[index-id='" + index_id + "']").find("textarea[type='textarea']").attr('name');
                        //                     tmp_local_storage.descriptive[descriptive_id] = $("div[index-id='" + index_id + "']").find("textarea[type='textarea']").val();
                        //                 }
                        //             } else {
                        //                 change_que(next_id);
                        //                 var descriptive_id = $("div[index-id='" + index_id + "']").find("textarea[type='textarea']").attr('name');
                        //                 tmp_local_storage.descriptive[descriptive_id] = $("div[index-id='" + index_id + "']").find("textarea[type='textarea']").val();
                        //             }
                        //         } else if (configure_data.question_types[index_id] == "blank") {
                        //             if (configure_data.que_required == 1) {
                        //                 if ($(".question[index-id=" + index_id + "]").find("input[type='text']").val() == '') {
                        //                     required_error();
                        //                     return false;
                        //                 } else {
                        //                     change_que(next_id);
                        //                     var blank_id = $("div[index-id='" + index_id + "']").find("input[type='text']").attr('name');
                        //                     tmp_local_storage.blank[blank_id] = $("div[index-id='" + index_id + "']").find("input[type='text']").val();
                        //                 }
                        //             }
                        //             else {
                        //                 change_que(next_id);
                        //                 var blank_id = $("div[index-id='" + index_id + "']").find("input[type='text']").attr('name');
                        //                 tmp_local_storage.blank[blank_id] = $("div[index-id='" + index_id + "']").find("input[type='text']").val();
                        //             }
                        //         }
                        //     } else {
                        //         // when quiz question required show error Answer is required
                        //         if (configure_data.que_required == 1) {
                        //             if (($("input[name='answer']:checked").length == 0 && $("input[type='radio']").length >= 1) ||
                        //                 ($("input[name='answer']").val() == '' && $("input[name='answer']").length == 1) ||
                        //                 ($("textarea[name='answer']").val() == '' && $("textarea[name='answer']").length == 1)) {
                        //                 required_error();
                        //             }
                        //             else {
                        //                 // required_error();
                        //                 $('#quiz_err_info').html('');
                        //             }
                        //         }
                        //     }
                        //     if (configure_data.prev_allow == 1) {
                        //         var que_grid = $(".que_grid");
                        //         que_grid.css({
                        //             'pointer-events': 'none',
                        //             'cursor': 'default'
                        //         });
                        //     }

                        //     window.localStorage.setItem("quiz", JSON.stringify(tmp_local_storage));
                        //     if ($(this).attr('class').indexOf('quiz_finish') >= 0) {
                        //         delete localStorage["quiz"];
                        //         if (configure_data.que_required == 1 ||
                        //             ($("input[name='answer']:checked").length != 0 && $("input[type='radio']").length >= 1) ||
                        //             ($("input[name='answer']").val() != '' && $("input[name='answer']").length == 1) ||
                        //             ($("textarea[name='answer']").val() != '' && $("textarea[name='answer']").length == 1)) {
                        //             $("input[type='radio']").removeAttr('disabled');
                        //             if ($('#from_quiz').length != 0) {
                        //                 $('#from_quiz').submit();
                        //             } else {
                        //                 console.log($("textarea[name='answer']").length)

                        //                 $('#from_quiz_dynamic').submit();
                        //             }
                        //         }
                        //         else{
                        //             if ($('#from_quiz').length != 0) {
                        //                 $('#from_quiz').submit();
                        //             } else {
                        //                 $('#from_quiz_dynamic').submit();
                        //             }

                        //         }
                        //     }
                        // });
                        //perform prev question
                        $(document).on('click', '.quiz_prv', function (e) {
                            $('#quiz_err_info').html('');
                            var prev_id = $(this).attr('prev-id');
                            change_que(prev_id);
                        });
                        //change question throgh grid
                        $('.que_grid').on('click', function (e) {
                            var que_id = $(this).attr('grid-index-id');
                            var index_id = $('.que_active').attr('grid-index-id');
                            var radio_grp = $("div[index-id='" + index_id + "']").find("input[type='radio']");
                            var radio_grp_name = $(radio_grp[0]).attr('name');
                            if ($("input[name='" + radio_grp_name + "']:checked").length > 0) {
                                $("div[grid-index-id='" + index_id + "']").addClass('que_answered');
                                tmp_local_storage.checked_boxes[radio_grp_name] = $("input[name='" + radio_grp_name + "']:checked").attr('id');
                                window.localStorage.setItem("quiz", JSON.stringify(tmp_local_storage));
                            }
                            $('.que_grid').removeClass('que_active');
                            $(this).addClass('que_active');
                            change_que(que_id);
                            if(tmp_local_storage){
                               tmp_local_storage.current_que_id = que_id;
                            }
                        });
                    } else {
                        var tmp_local_storage = {};
                        tmp_local_storage.checked_boxes = {};
                        tmp_local_storage.blank = {};
                        tmp_local_storage.descriptive = {};
                        tmp_local_storage.current_que_id = null;
                        window.localStorage.setItem("quiz", JSON.stringify(tmp_local_storage));
                        if (localStorage.getItem("quiz") !== null) {
                            tmp_local_storage = JSON.parse(window.localStorage.getItem("quiz"));
                            for (var i in tmp_local_storage.checked_boxes) {
                                $('#' + tmp_local_storage.checked_boxes[i]).attr('checked', 'true');
                                if (configure_data.prev_readonly == 1) {
                                    var radio_grp = $('#' + tmp_local_storage.checked_boxes[i]).attr('name');
                                    if ($("input[name='" + radio_grp + "']:checked").length > 0) {
                                        var radios = $("input[name='" + radio_grp + "']")
                                        for (var i = 0; i < radios.length; i++) {
                                            radios[i].disabled = true;
                                        }
                                    }
                                }
                            }
                        }

                        if (configure_data.que_required == 1) {
                            $("input[type='radio']").attr('required', true);
                        }

                        $("input[type='radio']").click(function (e) {
                            var radio_grp = $(this).attr('name');
                            if (configure_data.prev_readonly == 1) {
                                if ($("input[name='" + radio_grp + "']:checked").length > 0) {
                                    var radios = $("input[name='" + radio_grp + "']")
                                    for (var i = 0; i < radios.length; i++) {
                                        radios[i].disabled = true;
                                    }
                                }
                            }
                            tmp_local_storage.checked_boxes[radio_grp] = $(this).attr('id');
                            window.localStorage.setItem("quiz", JSON.stringify(tmp_local_storage));
                        });

                        $(document).on('click', ".quiz_finish", function (e) {
                            if ($('#from_quiz')[0].checkValidity() == true || configure_data.que_required == 0) {
                                if ($('#from_quiz').length != 0) {
                                    $('#from_quiz').submit();
                                } else {
                                    $('#from_quiz_dynamic').submit();
                                }
                            }
                            else {
                                document.getElementById("from_quiz").reportValidity();
                            }
                        });
                    }
                });
            function change_que(change_id) {
                $('#quiz_err_info').html('');
                tmp_local_storage.current_que_id = parseInt(change_id);
                var index_id = $('.que_show').attr('index-id');
                $("div[index-id='" + index_id + "']").addClass('que_hide').removeClass('que_show');
                $("div[index-id='" + change_id + "']").addClass('que_show').removeClass('que_hide');
                // for grid
                $("div[grid-index-id='" + index_id + "']").removeClass('que_active');
                $("div[grid-index-id='" + change_id + "']").addClass('que_active');
            }
            function required_error() {
                $('#quiz_err_info').html('<div class="alert alert-danger">' + '<strong>Error!</strong> Answer is required ' + '</div>');
            }
        }
    };
    start_quiz();
    return start_quiz
});
