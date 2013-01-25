var interval = 1000;
var cancelled = false;
var submit_button = null;
var cancel_button = null;
var reboot_button = null;
var button_type = null;
var messages_box = null;
var progress_bar_container = null;
var installation_messages = null;
var install_form = null;
var bar = null;
var amount = null;
var tour_box = null;


function disable_submit() {
    submit_button.addClass('inactive');
    submit_button.attr("disabled", "disabled");
    cancel_button.removeClass('inactive');
    cancel_button.removeAttr("disabled");
}

function disable_cancel() {
    cancel_button.addClass('inactive');
    cancel_button.attr("disabled", "disabled");
}


function enable_submit() {
    submit_button.removeClass('inactive');
    submit_button.removeAttr("disabled");
    cancel_button.addClass('inactive');
    cancel_button.attr("disabled", "disabled");
}

function show_progress(data) {
    bar.width(517 * (data / 100.0));
    amount.html(data + '%');
}


/* handling process states */

function process_error(data)
{
    progress_bar_container.hide();
    tour_box.hide();
    messages_box.removeClass('success');
    messages_box.addClass('error');
    messages_box.html(data.message)
    messages_box.show();
    enable_submit();
}

function process_running(data)
{
    var value = data.progress / 1.0;
    show_progress(value);
    setTimeout("get_progress()",interval);
    installation_messages.html(data.message)
}

function process_finished(data)
{
    progress_bar_container.hide();
    tour_box.hide();
    messages_box.removeClass('error');
    messages_box.addClass('success');
    messages_box.html('Congratulations! Your Amahi HDA is installed! <br/>However you <b>must reboot</b> your HDA to make it fully operational.<br/>After rebooting, check that your HDA works to your satisfaction,<br/>by accessing it at <div align="center"><big><b><a target="_blank" href="http://hda">http://hda</a></b></big></div><br/>Then you may optionally turn off your router\'s DHCP server,<br/>(and reboot your other systems), to take full advantage of the capabilities of your HDA.');
    messages_box.show();
    reboot_button.show();
    install_form.hide();
    disable_cancel();
}

/* end handling process states */


function start_installation() {
    bar.width(0);
    reboot_button.hide();
    $.post('/install',
                install_form.serialize(),
                function(data) {
                    var obj = eval("("+data+")");
                    if (obj.status == 'running') {
                        progress_bar_container.show();
                        tour_box.show();
                        $("#main-photo-slider").codaSlider();
                        run_slider();
                        setTimeout("get_progress()",interval);
                    } else {
                        progress_bar_container.hide();
                        messages_box.removeClass('success');
                        messages_box.addClass('error');
                        messages_box.html(obj.message);
                        messages_box.show();
                        enable_submit();
                    }

                });
}

function cancel_installation() {
    progress_bar_container.hide();
    tour_box.hide();
    $.post('/cancel',
           install_form.serialize());
}

function get_progress(){
    $.post('/check-progress',
        null,
        function(data) {
            var obj = eval("("+data+")");
            switch(obj.status) {
            case 'error':
                process_error(obj)
                break;
            case 'running':
                process_running(obj)
                break;
            case 'finished':
                process_finished(obj)
                $("#code-input").val('');
            }
        });
}


$(document).ready(function() {
    submit_button = $("#submit_button");
    cancel_button = $("#cancel_button");
    reboot_button = $("#reboot-wrapper");
    button_type = $("#button_type");
    messages_box = $("#messages");
    progress_bar_container = $("#progress-bar-container");
    installation_messages = $("#installation-messages");
    install_form = $("#install-form");
    bar = $("#bar");
    amount = $("#progress-amount");
    tour_box = $("#tour-box");

    install_form.submit(function() {
        messages_box.hide();
        
        if (button_type.val() == 'submit') {
            disable_submit();
            cancelled = false;

            start_installation()
            return false;
        } else {
            enable_submit();
            cancelled = true;

            cancel_installation()
            return false;
        }
        
    });

    $("#code-input").focus(function() {if (! ($(this).hasClass('focused'))) {$(this).val('');$(this).addClass('focused');}});
    $("#code-input").blur(function() {if ($(this).val() == '') {$(this).val('This HDA\'s Install Code');$(this).removeClass('focused');}});
});
