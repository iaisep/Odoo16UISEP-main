odoo.define('openeducat_quiz_anti_cheating.website_anti_cheating_quiz', function (require) {

var core = require('web.core');
var session = require('web.session');
var ajax = require('web.ajax');
var rpc = require('web.rpc');
var _t = core._t;
var Dialog = require('web.Dialog');
var qweb = core.qweb;

$( document ).ready(function() {

            async function run_cam() {
                  await changeFaceDetector(TINY_FACE_DETECTOR)
                  changeInputSize(128)
                  var stream = this;
                  var mediaDevices = navigator.mediaDevices;
                  try {
                        $('.btn-start-exam').bind('click', false);
                        stream = await navigator.mediaDevices.getUserMedia({ video: true,});
                        const videoEl = $('#inputVideo').get(0)
                              if (videoEl){
                                $('.btn-start-exam').unbind('click');
                                videoEl.srcObject = stream
                              }
                      } catch(err) {
                           $("a").prop("href", "/online-exams");
                           $('.btn-start-exam').unbind('click');
                        return ajax.jsonRpc('/camera/access','call',{});
                      }
            }

            var start_quiz = $( "a" ).hasClass( "quiz_prv" )
            if (start_quiz){
                var exam_id = $("input[name='ExamID']").val();
                session.rpc("/quiz/config", {result_id:exam_id})
                   .then(function(configure_data) {
                        if(configure_data.face_tracking == 1){
                        run_cam()
                        }
                   });
            }

            let forwardTimes = []
            function updateTimeStats(timeInMs) {
              forwardTimes = [timeInMs].concat(forwardTimes).slice(0, 30)
              const avgTimeInMs = forwardTimes.reduce((total, t) => total + t) / forwardTimes.length
              $('#time').val(`${Math.round(avgTimeInMs)} ms`)
              $('#fps').val(`${faceapi.round(1000 / avgTimeInMs)}`)
            }

            async function onPlay() {
                  const videoEl = $('#inputVideo').get(0)
                  if(videoEl.paused || videoEl.ended || !isFaceDetectionModelLoaded())
                    return setTimeout(() => onPlay())

                  const options = getFaceDetectorOptions()
                  const ts = Date.now()
                  const result = await faceapi.detectSingleFace(videoEl, options)
                  updateTimeStats(Date.now() - ts)
                  if (result) {
                    const canvas = $('#overlay_start').get(0)
                    const dims = faceapi.matchDimensions(canvas, videoEl, true)
                    faceapi.draw.drawDetections(canvas, faceapi.resizeResults(result, dims))
                  }
                setTimeout(() => onPlay())
            }

        var s_quiz = $( "a" ).hasClass( "btn-start-exam" )
        if (s_quiz){
            var result_id = $("input[name='result']").val();
            session.rpc("/quiz/config", {result_id:result_id})
           .then(function(configure_data) {
                if(configure_data.face_tracking == 1){
                            $( ".card" ).addClass("float-start")
//                            $(".card").css({"height": "234px","width": "795px"});
                            var card_height = $(".card").outerHeight()
                            $( "<div class='col-lg-3 pe-0'>"+
                               "<div class='progress' id='loader'><div class='indeterminate'></div></div>"+
                               "<div class='card' style='position: relative'>"+
                               '<video  id="inputVideo" width="312" height="auto"'+ card_height +'" autoplay muted></video>'+
                               "</div>").insertAfter( $( ".card" ) );
                            var video_height = $("video").width() - 5
                            $("<canvas id='overlay_start' style='width:315px; height:234px;'/></div>").insertAfter("#inputVideo");
                            const video = document.querySelector('#inputVideo');
                            video.onloadedmetadata = (event) => {
                                  onPlay(self);
                                  $(".success_camera").remove()
                                  $(".quiz_starting_page").prepend("<div class='container success_camera px-0'><div class='alert alert-success alert-dismissible fade show'><strong>Camera access successfully.</strong> You are being tracked by the administration."+
                                                                    "</div></div>");
                            };
                            initFaceDetectionControls()
                }
           });
           session.rpc("/check/state",{result_id:result_id}).then(function(data) {
               if (data){
                    $(".btn-start-exam").removeAttr("href");
                    $(".btn-start-exam").attr("href","/quiz/hold");
               }
           });
        }

    var exam_id = $("input[name='config_data']").val();
    if(exam_id !== undefined){
        var self = this;
        session.rpc("/quiz/config", {result_id:exam_id})
           .then(function(configure_data) {
                href = window.location.href
                var quiz_rule = href.split('attempt/')
                // var x = document.getElementById("submit_exam").href;
                // var y = x.lastIndexOf('/');
                // var res = x.substring(y+1);

// face tracking with warnings
                if(configure_data.face_tracking == 1){
                    if (configure_data.warning_state != 'open'){
                    var colorScale = d3.scaleLinear()
                        .range(["green","yellow","red"])
                        .domain([0,(configure_data.warning_limit - 1)/2, configure_data.warning_limit - 1]);
                    }
                    let forwardTimes = []
                    var warning_count = 0
                    function updateTimeStats(timeInMs) {
                      forwardTimes = [timeInMs].concat(forwardTimes).slice(0, 30)
                      const avgTimeInMs = forwardTimes.reduce((total, t) => total + t) / forwardTimes.length
                      $('#time').val('${Math.round(avgTimeInMs)} ms')
                      $('#fps').val('${faceapi.round(1000 / avgTimeInMs)}')
                    }

                    async function run() {

                          await changeFaceDetector(TINY_FACE_DETECTOR)
                          changeInputSize(128)

                          try {
                                $('#hide').attr('disabled','disabled');
                                const stream = await navigator.mediaDevices.getUserMedia({ video: true,});
                                const videoEl = $('#inputVideo').get(0)
                                      if (videoEl){
                                        $('#hide').removeAttr('disabled');
                                        videoEl.srcObject = stream
                                      }
                          } catch(err) {
                                    $('#hide').removeAttr('disabled');
                                    $('#hide').removeClass('quiz_nxt');
                                    window.location = '/online-exams'
                                    return ajax.jsonRpc('/camera/access','call',{});
                          }
                        }
                    function updateResults() {}

                    async function onPlay() {
                       const videoEl = $('#inputVideo').get(0)
                       if(videoEl.paused || videoEl.ended || !isFaceDetectionModelLoaded()){
                                return setTimeout(() => onPlay())
                       }
                       const options = new faceapi.TinyFaceDetectorOptions({ scoreThreshold: configure_data.sensitivity })
                       const ts = Date.now()
                       const result = await faceapi.detectAllFaces(videoEl, options)
                       updateTimeStats(Date.now() - ts)
                       if (configure_data.warning_state != 'open'){
                           for (i = 0; i < sessionStorage.warning_count; i++) {
                                      $(".item"+i).css("background-color", colorScale(i));
                           }
                       }
                       if ((result.length) == 1) {
                            const canvas = $('#overlay').get(0)
                            const dims = faceapi.matchDimensions(canvas, videoEl, true)
                            faceapi.draw.drawDetections(canvas, faceapi.resizeResults(result, dims))
                       }
                       else if((result.length) > 1){
                            if (configure_data.warning_limit <= parseInt(sessionStorage.getItem("warning_count"))){
                                if (configure_data.warning_state != 'open'){
                                    sessionStorage.removeItem('warning_count');
                                    $("a[title='home']").removeAttr("href");
                                    $("a[title='home']").attr("href","/quiz/hold");
                                    $('a[title="home"]')[0].click();
                                    return ajax.jsonRpc("/warning/quite",'call',{
                                        'result_id': exam_id,
                                        'warning_state': configure_data.warning_state,
                                    });
                                }
                            }
                            var canvas=$('#overlay')[0];
                            if(configure_data.face_tracking == 1){
                                canvas.getContext('2d').drawImage($('#inputVideo')[0],0,0,650,500);
                                var f=canvas.toDataURL();
                            }

                            var receipt_data = html2canvas(document.querySelector("#wrapwrap"))
                                    .then(function(canvas){
                                    var img = canvas.toDataURL().split(',')[1];

                                var warning_count = sessionStorage.getItem("warning_count");
                                warning_count++;
                                sessionStorage.warning_count = warning_count;
                                sessionStorage.getItem("warning_count",sessionStorage.getItem("warning_count"));
                                alert( _t('External Person detected.\nWarning Number:'+ sessionStorage.getItem("warning_count")))
                                     var timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                                var d = new Date();
                                var time = d.getHours() + ":" + d.getMinutes() + ":" + d.getSeconds();
                                ajax.jsonRpc("/warning/line",'call',{
                                            'file': img,
                                            'result_id': exam_id,
                                            'warning_no': sessionStorage.getItem("warning_count"),
                                            'timezone': timezone,
                                            'w_name': 'External Person detected.',
                                            'time': time,
                                });
                            });
                            if (configure_data.warning_state != 'open'){
                                for (i = 0; i < warning_count; i++) {
                                      $(".item"+i).css("background-color", colorScale(i));
                                }
                            }
                       }
                       else{
                            if (configure_data.warning_limit <= parseInt(sessionStorage.getItem("warning_count"))){
                                if (configure_data.warning_state != 'open'){
                                    sessionStorage.removeItem('warning_count');
                                    $("a[title='home']").removeAttr("href");
                                    $("a[title='home']").attr("href","/quiz/hold");
                                    $('a[title="home"]')[0].click();
                                    return ajax.jsonRpc("/warning/quite",'call',{
                                        'result_id': exam_id,
                                        'warning_state': configure_data.warning_state,
                                    });
                                }
                            }
                            var canvas=$('#overlay')[0];
                            if(configure_data.face_tracking == 1){
                                canvas.getContext('2d').drawImage($('#inputVideo')[0],0,0,650,500);
                                var f=canvas.toDataURL();
                            }

                            var receipt_data = html2canvas(document.querySelector("#wrapwrap"))
                                    .then(function(canvas){
                                    var img = canvas.toDataURL().split(',')[1];

                                    var warning_count = sessionStorage.getItem("warning_count");
                                    warning_count++;
                                    sessionStorage.warning_count = warning_count;
                                    sessionStorage.getItem("warning_count",sessionStorage.getItem("warning_count"));
                                    window.alert( _t('You have moved out from current exam window.\nYou are not allowed to Move out from Exam page.\n\nWarning Number:'+ sessionStorage.getItem("warning_count")))
                                    var timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                                    var d = new Date();
                                    var time = ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2) + ":" + ("0" + d.getSeconds()).slice(-2);
                                    ajax.jsonRpc("/warning/line",'call',{
                                                'file': img,
                                                'result_id': exam_id,
                                                'warning_no': sessionStorage.getItem("warning_count"),
                                                'timezone': timezone,
                                                'w_name': 'Move out from Exam page.',
                                                'time': time,
                                            });
                            });
                            if (configure_data.warning_state != 'open'){
                                for (i = 0; i < warning_count; i++) {
                                      $(".item"+i).css("background-color", colorScale(i));
                                }
                            }

                       }
                       setTimeout(() => onPlay(), 500);
                    }

                    function updateResults() {}
                    $( "<div class='progress' id='loader'><div class='indeterminate'></div></div>"+
                       "<div class='card' style='position: relative'>"+
                       '<video  id="inputVideo" width="256" height="193" autoplay muted></video>'+
                       "<canvas id='overlay'/></div>").appendTo( $( ".que_grid" ) );
                    const video = document.querySelector('#inputVideo');

                    if (configure_data.warning_state != 'open'){
                        $("<div class='container' id='w_count'>"+
                                   "<h5 style='margin-top:10px'>Warning</h5>"+
                                      "<div class='progress-segment'>"+
                                      "</div>"+
                                   "</div>").insertBefore( $( ".progress" ) );
                    }
                    const canvas = $('#overlay').get(0)
                    video.onloadedmetadata = (event) => {
                      onPlay(self);
                    };
                    initFaceDetectionControls()
                    run()
                    for (i = 0; i < configure_data.warning_limit ; i++) {
                              $("<div class='item item"+i+"'></div>").appendTo($(".progress-segment"));
                            }
                    $( "#final_finish" ).click(function() {
                        sessionStorage.removeItem('warning_count');
                    });
               }

// copy paste allow
               if(configure_data.copy_paste_allow == 0){
                   $('#from_quiz_dynamic').bind("cut copy paste",function(e) {
                         e.preventDefault();
                   });
               }

// take screenshot in random
               if(configure_data.take_screenshot == 0){
                    var random_end = configure_data.random_end * 58000 ;
                    var random_start = configure_data.random_start * 58000 ;
                    function randRange() {
                           var newTime = Math.floor(Math.random() * random_end - random_start);
                           if (newTime < 0 ){
                                newTime = -(newTime)
                           }
                           return newTime;
                    }
                    function imageData(){
                        var d = new Date();
                        var n = d.toLocaleTimeString();
                        var canvas=$('#overlay')[0];
                        if(configure_data.face_tracking == 1){
                        canvas.getContext('2d').drawImage($('#inputVideo')[0],10,10,650,500);
                        var f=canvas.toDataURL();
                        }
                        var receipt_data = html2canvas(document.querySelector("#from_quiz_dynamic"))
                            .then(function(canvas){
                                var img = canvas.toDataURL().split(',')[1];
                                let blob = new Blob([img], {type: 'image/png'});
                                var fileReader = new FileReader();
                                var file = base64js.fromByteArray(new Uint8Array(fileReader.result));
                                fileReader.onload = function(){
                                    return ajax.jsonRpc('/create/attachment','call',{
                                        'file': base64js.fromByteArray(new Uint8Array(fileReader.result)),
                                        'file_name': 'image',
                                        'name': 'image',
                                        'exam': exam_id
                                    });
                                }
                                fileReader.readAsArrayBuffer(blob);
                                localStorage.setItem("img", img);
                            });
                    }
                    function toggleSomething(){
                        var d = new Date();
                        var n = d.toLocaleTimeString();
                       var timer2 = setTimeout(imageData, randRange());
                    }
                    var timer1 = setInterval(toggleSomething, random_end);
               }else if(configure_data.take_screenshot == 1){
// take screenshot in time interval
                    var time = configure_data.particular_interval * 58000;
                    setInterval(function(){
                        var canvas=$('#overlay')[0];
                        if(configure_data.face_tracking == 1){
                            canvas.getContext('2d').drawImage($('#inputVideo')[0],10,10,650,500);
                            var f=canvas.toDataURL();
                        }
                        var receipt_data = html2canvas(document.querySelector("#wrapwrap"))
                                .then(function(canvas){
                                 var img = canvas.toDataURL().split(',')[1];
                                    let blob = new Blob([img], {type: 'image/png'});
                                    var fileReader = new FileReader();
                                    var file = base64js.fromByteArray(new Uint8Array(fileReader.result));
                                    fileReader.onload = function(){
                                        return ajax.jsonRpc('/create/attachment','call',{
                                            'file': base64js.fromByteArray(new Uint8Array(fileReader.result)),
                                            'file_name': 'image',
                                            'name': 'image',
                                            'exam': exam_id
                                        });
                                    }
                                    fileReader.readAsArrayBuffer(blob);
                                    localStorage.setItem("img", img);
                                    });
                    }, time);
            }

 //question time out
                if (configure_data.question_count != 0 && configure_data.question_time_out != 0){
                       var time_out = configure_data.question_time_out * 60000;
                       var myVar = setTimeout(function(){
                            if ($('#hide').length > 0) {
                                document.getElementById('hide').click();
                            }
                            if ($('#final_finish').length > 0) {
                                document.getElementById('final_finish').click();
                            }
                      }, time_out);
                }
          });
    }
});
});
