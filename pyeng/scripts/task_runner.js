
function init_type1(data) {

	var p = $('<p></p>').appendTo(document.body);
	p.html(data['given']);

	var answers = JSON.parse(data['answers']);

	for (var i = 0; i < answers.length; i++) {

		var gap = $('<span class="gap"></span>');

		var text = answers[i];
		var full = false;
		if (text.length > 1 && text.substring(text.length - 2) === '##') {
			text = text.substring(0, text.length - 2);
			full = true;
		}

		gap.append('<span class="good_part">' + text + "</span>");
		gap.append('<input type="text">');

		if (full)
			gap.find('input').hide();

		p.html(p.html().replace('##', '<span class="gap">' + gap.html() + "</span>"));
	}

	$('<button>Завершить</button>').appendTo(document.body).
		on('click', stop);

	$('.gap input').on('input', checkLetter);

	$('<div class="time"></div>').appendTo(document.body);
	$('<div class="result"></div>').appendTo(document.body);

	setTime(Number(data['time_left']));
	setResult(Number(data['result']));
	setInterval(tick, 1000);
}

function tick() {

	window.timeLeft--;
	$('.time').html(window.timeLeft);
	if (window.timeLeft === 0)
		stop();

}

function setTime(timeLeft) {

	$('.time').html(timeLeft);
	window.timeLeft = timeLeft;

}

function setResult(result) {

	$('.result').html(result);

}

function checkLetter(event) {

	var my_input = this;
	var my_gap = $(my_input).parent();
	var my_good_part = $(my_gap).find('.good_part');
	var all_inputs = $('.gap input');

	all_inputs.prop('disabled', true);

	var letter = $(my_input).val();
	if (letter.length > 1) {
		$(my_input).val($(my_input).val().substring(0, 1));
		all_inputs.prop('disabled', false);
		$(my_input).focus();
		return;
	}

	if (letter.length === 0) {
		all_inputs.prop('disabled', false);
		$(my_input).focus();
		return;
	}

	$(my_input).css('color', 'black');


	$.post('task_runner', {
		command: 'input',
		student_task: window.STUDENT_TASK_ID,
		gap_nom: $('.gap').index(my_gap),
		letter: letter
	}, function(data) {
		data = JSON.parse(data);

		checkThrowers(data);

		all_inputs.prop('disabled', false);

		if (data['command'] === 'good') {
			$(my_good_part).html($(my_good_part).html() + letter);
			$(my_input).val('');
		}
		else {
			$(my_input).css('color', 'red');
		}

		if (data['full_word'] === 'true')
			$(my_input).hide();
		else
			$(my_input).focus();

		setTime(Number(data['time_left']));
		setResult(Number(data['result']));

	});

}

function stop() {

	$.post('task_runner', {command: 'end', student_task: window.STUDENT_TASK_ID},
	        function(data) {
	            document.location.href = '/';
	        });

}

function checkThrowers(data) {
	if (data['command'] == 'to_index')
		document.location.href = '/';
}
 
function init(data) {
	data = JSON.parse(data);
	checkThrowers(data);
	if (data["task_type"] === 1)
		init_type1(data);
}

$(function() {
	$.post('task_runner', {command: 'init',
								student_task: window.STUDENT_TASK_ID},
		init);

});