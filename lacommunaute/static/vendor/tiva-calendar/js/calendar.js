// Variable
var thisDate = 1;
var today = new Date();
var todaysDay = today.getDay() + 1;
var todaysDate = today.getDate();
var todaysMonth = today.getMonth() + 1;
var todaysYear = today.getFullYear();

var firstDate;
var firstDay;
var lastDate;
var numbDays;
var numevents = 0;
var daycounter = 0;
var calendarString = "";

var monthNum_full = todaysMonth;
var yearNum_full = todaysYear;
var monthNum_compact = todaysMonth;
var yearNum_compact = todaysYear;

var tiva_events = [];
var order_num = 0;

// Config variable
var wordDay;
var date_start;

function getShortText(text, num) {
	if (text) {
		// Get num of word
		var textArray = text.split(" ");
		if (textArray.length > num) {
			return textArray.slice(0, num).join(" ") + " ...";
		}
		return text;
	}
	return "";
}

function sortEventsByDate(a, b) {
	if (a.date < b.date) {
		return -1;
	} else if (a.date > b.date) {
		return 1;
	} else {
		return 0;
	}
}

function sortEventsByUpcoming(a, b) {
	var today_date = new Date(todaysYear, todaysMonth - 1, todaysDate);
	if (Math.abs(a.date - today_date.getTime()) < Math.abs(b.date - today_date.getTime())) {
		return -1;
	} else if (Math.abs(a.date - today_date.getTime()) > Math.abs(b.date - today_date.getTime())) {
		return 1;
	} else {
		return 0;
	}
}

function getEventsByTime(type) {
	var events = [];
	var today_date = new Date(todaysYear, todaysMonth - 1, todaysDate);
	for (var i = 0; i < tiva_events.length; i++) {
		if (type == 'upcoming') {
			if (tiva_events[i].date >= today_date.getTime()) {
				events.push(tiva_events[i]);
			}
		} else {
			if (tiva_events[i].date < today_date.getTime()) {
				events.push(tiva_events[i]);
			}
		}
	}
	return events;
}

// Change month or year on calendar
function changedate(btn, layout) {
	if (btn == "prevyr") {
		eval("yearNum_" + layout + "--;");
	} else if (btn == "nextyr") {
		eval("yearNum_" + layout + "++;");
	} else if (btn == "prevmo") {
		eval("monthNum_" + layout + "--;");
	} else if (btn == "nextmo") {
		eval("monthNum_" + layout + "++;");
	} else if (btn == "current") {
		eval("monthNum_" + layout + " = todaysMonth;");
		eval("yearNum_" + layout + " = todaysYear;");
	}

	if (monthNum_full == 0) {
		monthNum_full = 12;
		yearNum_full--;
	} else if (monthNum_full == 13) {
		monthNum_full = 1;
		yearNum_full++
	}

	if (monthNum_compact == 0) {
		monthNum_compact = 12;
		yearNum_compact--;
	} else if (monthNum_compact == 13) {
		monthNum_compact = 1;
		yearNum_compact++
	}

	// Get first day and number days of month
	eval("firstDate = new Date(yearNum_" + layout + ", monthNum_" + layout + " - 1, 1);");
	if (date_start == 'sunday') {
		firstDay = firstDate.getDay() + 1;
	} else {
		firstDay = firstDate.getDay();
	}
	eval("lastDate = new Date(yearNum_" + layout + ", monthNum_" + layout + ", 0);");
	numbDays = lastDate.getDate();

	// Create calendar
	eval("createCalendar(layout, firstDay, numbDays, monthNum_" + layout + ", yearNum_" + layout + ");");

	return;
}

// Create calendar
function createCalendar(layout, firstDay, numbDays, monthNum, yearNum) {
	calendarString = '';
	daycounter = 0;

	calendarString += '<table class=\"calendar-table table table-bordered\">';
	calendarString += '<tbody>';
	calendarString += '<tr>';
	if (layout == 'full') {
		calendarString += '<td class=\"calendar-btn\"><span onClick=\"changedate(\'prevmo\', \'full\')\">« <span class="btn-change-date">' + prev_month + '<\/span><\/span><\/td>';
		calendarString += '<td class=\"calendar-title\" colspan=\"5\"><span><i class=\"fa fa-calendar-o\"><\/i>' + wordMonth[monthNum - 1] + '&nbsp;&nbsp;' + yearNum + '<\/span><\/td>';
		calendarString += '<td class=\"calendar-btn\"><span onClick=\"changedate(\'nextmo\', \'full\')\"><span class="btn-change-date">' + next_month + '<\/span> »<\/span><\/td>';
	} else {
		calendarString += '<td class=\"calendar-btn\"><span onClick=\"changedate(\'prevmo\', \'compact\')\">«<\/span><\/td>';
		calendarString += '<td class=\"calendar-title\" colspan=\"5\"><span>' + wordMonth[monthNum - 1] + '&nbsp;&nbsp;' + yearNum + '<\/span><\/td>';
		calendarString += '<td class=\"calendar-btn\"><span onClick=\"changedate(\'nextmo\', \'compact\')\">»<\/span><\/td>';
	}
	calendarString += '<\/tr>';

	calendarString += '<tr class="active">';
	for (var m = 0; m < wordDay.length; m++) {
		calendarString += '<th>' + wordDay[m].substring(0, 3) + '<\/th>';
	}
	calendarString += '<\/tr>';

	thisDate == 1;

	for (var i = 1; i <= 6; i++) {
		var k = (i - 1) * 7 + 1;
		if (k < (firstDay + numbDays)) {
			calendarString += '<tr>';
			for (var x = 1; x <= 7; x++) {
				daycounter = (thisDate - firstDay) + 1;
				thisDate++;
				if ((daycounter > numbDays) || (daycounter < 1)) {
					calendarString += '<td class=\"calendar-day-blank\">&nbsp;<\/td>';
				} else {
					// Saturday or Sunday
					if (date_start == 'sunday') {
						if ((x == 1) || (x == 7)) {
							daycounter_s = '<span class=\"calendar-day-weekend\">' + daycounter + '</span>';
						} else {
							daycounter_s = daycounter;
						}
					} else {
						if ((x == 6) || (x == 7)) {
							daycounter_s = '<span class=\"calendar-day-weekend\">' + daycounter + '</span>';
						} else {
							daycounter_s = daycounter;
						}
					}

					if ((todaysDate == daycounter) && (todaysMonth == monthNum)) {
						calendarString += '<td class=\"calendar-day-normal calendar-day-today\">';
					} else {
						calendarString += '<td class=\"calendar-day-normal\">';
					}
					if (checkEvents(daycounter, monthNum, yearNum)) {
						if (layout == 'full') {
							calendarString += '<div class=\"calendar-day-event\">';
						} else {
							calendarString += '<div class=\"calendar-day-event\" onmouseover=\"showTooltip(0, \'compact\', ' + daycounter + ', ' + monthNum + ', ' + yearNum + ', this)\" onmouseout=\"clearTooltip(\'compact\', this)\" onclick=\"showEventDetail(0, \'compact\', ' + daycounter + ', ' + monthNum + ', ' + yearNum + ')\">';
						}
						calendarString += daycounter_s;

						// Get events of day
						if (layout == 'full') {
							var events = getEvents(daycounter, monthNum, yearNum);
							for (var t = 0; t < events.length; t++) {
								if (typeof events[t] != "undefined") {
									var color = events[t].color ? events[t].color : 1;
									var event_class = "one-day";
									if (events[t].first_day && !events[t].last_day) {
										event_class = "first-day";
									} else if (events[t].last_day && !events[t].first_day) {
										event_class = "last-day";
									} else if (!events[t].first_day && !events[t].last_day) {
										event_class = "middle-day";
									}

									calendarString += '<div class=\"calendar-event-name ' + event_class + ' color-' + color + '\" id=\"' + events[t].id + '\" onmouseover=\"showTooltip(' + events[t].id + ', \'full\', ' + daycounter + ', ' + monthNum + ', ' + yearNum + ', this)\" onmouseout=\"clearTooltip(\'full\', this)\" onclick=\"showEventDetail(' + events[t].id + ', \'full\', ' + daycounter + ', ' + monthNum + ', ' + yearNum + ')\"><span class="event-name">' + getShortText(events[t].name, 2) + '</span><\/div>';
								} else {
									var event_fake;
									if (typeof events[t + 1] != "undefined") {
										if (typeof tiva_events[events[t + 1].id - 1] != "undefined") {
											event_fake = getShortText(tiva_events[events[t + 1].id - 1].name, 2);
										} else {
											event_fake = "no-name";
										}
									} else {
										event_fake = "no-name";
									}
									calendarString += '<div class=\"calendar-event-name no-name\">' + event_fake + '</div>';
								}
							}
						} else {
							calendarString += '<span class="calendar-event-mark"></span>';
						}

						// Tooltip
						calendarString += '<div class=\"tiva-event-tooltip\"><\/div>';
						calendarString += '<\/div>';
					} else {
						calendarString += daycounter_s;
					}
					calendarString += '<\/td>';
				}
			}
			calendarString += '<\/tr>';
		}
	}
	calendarString += '</tbody>';
	calendarString += '</table>';

	if (layout == 'full') {
		jQuery('.tiva-calendar-full').html(calendarString);
	} else {
		jQuery('.tiva-calendar-compact').html(calendarString);
	}
	thisDate = 1;
}

// Check day has events or not
function checkEvents(day, month, year) {
	numevents = 0;
	var date_check = new Date(year, Number(month) - 1, day);
	for (var i = 0; i < tiva_events.length; i++) {
		var start_date = new Date(tiva_events[i].year, Number(tiva_events[i].month) - 1, tiva_events[i].day);
		var end_date = new Date(tiva_events[i].year, Number(tiva_events[i].month) - 1, Number(tiva_events[i].day) + Number(tiva_events[i].duration) - 1);
		if ((start_date.getTime() <= date_check.getTime()) && (date_check.getTime() <= end_date.getTime())) {
			numevents++;
		}
	}

	if (numevents == 0) {
		return false;
	} else {
		return true;
	}
}

function getOrderNumber(id, day, month, year) {
	var date_check = new Date(year, Number(month) - 1, day);
	var events = [];
	for (var i = 0; i < tiva_events.length; i++) {
		var start_date = new Date(tiva_events[i].year, Number(tiva_events[i].month) - 1, tiva_events[i].day);
		var end_date = new Date(tiva_events[i].year, Number(tiva_events[i].month) - 1, Number(tiva_events[i].day) + Number(tiva_events[i].duration) - 1);
		if ((start_date.getTime() <= date_check.getTime()) && (date_check.getTime() <= end_date.getTime())) {
			var first_day = (start_date.getTime() == date_check.getTime()) ? true : false;
			var event = { id: tiva_events[i].id, name: tiva_events[i].name, day: tiva_events[i].day, month: tiva_events[i].month, year: tiva_events[i].year, first_day: first_day };
			events.push(event);
		}
	}

	if (events.length) {
		if (events[0].id == id) {
			var num = order_num;
			order_num = 0;
			return num;
		} else {
			order_num++;
			for (var j = 0; j < events.length; j++) {
				if (events[j].id == id) {
					return getOrderNumber(events[j - 1].id, events[j - 1].day, events[j - 1].month, events[j - 1].year);
				}
			}

		}
	}

	return 0;
}

// Get events of day
function getEvents(day, month, year) {
	var n = 0;
	var date_check = new Date(year, Number(month) - 1, day);
	var events = [];
	for (var i = 0; i < tiva_events.length; i++) {
		var start_date = new Date(tiva_events[i].year, Number(tiva_events[i].month) - 1, tiva_events[i].day);
		var end_date = new Date(tiva_events[i].year, Number(tiva_events[i].month) - 1, Number(tiva_events[i].day) + Number(tiva_events[i].duration) - 1);
		if ((start_date.getTime() <= date_check.getTime()) && (date_check.getTime() <= end_date.getTime())) {
			var first_day = (start_date.getTime() == date_check.getTime()) ? true : false;
			var last_day = (end_date.getTime() == date_check.getTime()) ? true : false;
			var event = { id: tiva_events[i].id, name: tiva_events[i].name, first_day: first_day, last_day: last_day, color: tiva_events[i].color };

			if (!first_day) {
				n = getOrderNumber(tiva_events[i].id, tiva_events[i].day, tiva_events[i].month, tiva_events[i].year);
			}

			events[n] = event;
			n++;
		}
	}

	return events;
}

// Show tooltip when mouse over
function showTooltip(id, layout, day, month, year, el) {
	if (layout == 'full') {
		if (tiva_events[id].image) {
			var event_image = '<img src="' + tiva_events[id].image + '" alt="' + tiva_events[id].name + '" />';
		} else {
			var event_image = '';
		}
		if (tiva_events[id].time) {
			var event_time = '<div class="event-time">' + tiva_events[id].time + '</div>';
		} else {
			var event_time = '';
		}

		// Change position of tooltip
		var index = jQuery(el).parent().find('.calendar-event-name').index(el);
		var count = jQuery(el).parent().find('.calendar-event-name').length;
		var bottom = 32 + ((count - index - 1) * 25);
		jQuery(el).parent().find('.tiva-event-tooltip').css('bottom', bottom + 'px');

		jQuery(el).parent().find('.tiva-event-tooltip').html('<div class="event-tooltip-item">'
			+ event_time
			+ '<div class="event-name">' + tiva_events[id].name + '</div>'
			+ '<div class="event-image">' + event_image + '</div>'
			+ '<div class="event-intro">' + getShortText(tiva_events[id].description, 10) + '</div>'
			+ '</div>'
		);
		jQuery(el).parent().find('.tiva-event-tooltip').css('opacity', '1');
		jQuery(el).parent().find('.tiva-event-tooltip').css('-webkit-transform', 'translate3d(0,0,0) rotate3d(0,0,0,0)');
		jQuery(el).parent().find('.tiva-event-tooltip').css('transform', 'translate3d(0,0,0) rotate3d(0,0,0,0)');
	} else {
		jQuery(el).find('.tiva-event-tooltip').html('');
		var events = getEvents(day, month, year);
		for (var i = 0; i < events.length; i++) {
			if (typeof events[i] != "undefined") {
				if (tiva_events[events[i].id].image) {
					var event_image = '<img src="' + tiva_events[events[i].id].image + '" alt="' + tiva_events[events[i].id].name + '" />';
				} else {
					var event_image = '';
				}
				if (tiva_events[events[i].id].time) {
					var event_time = '<div class="event-time">' + tiva_events[events[i].id].time + '</div>';
				} else {
					var event_time = '';
				}

				jQuery(el).find('.tiva-event-tooltip').append('<div class="event-tooltip-item">'
					+ event_time
					+ '<div class="event-name">' + tiva_events[events[i].id].name + '</div>'
					+ '<div class="event-image">' + event_image + '</div>'
					+ '<div class="event-intro">' + getShortText(tiva_events[events[i].id].description, 10) + '</div>'
					+ '</div>'
				);
			}
		}
		jQuery(el).find('.tiva-event-tooltip').css('opacity', '1');
		jQuery(el).find('.tiva-event-tooltip').css('-webkit-transform', 'translate3d(0,0,0) rotate3d(0,0,0,0)');
		jQuery(el).find('.tiva-event-tooltip').css('transform', 'translate3d(0,0,0) rotate3d(0,0,0,0)');
	}
}

// Clear tooltip when mouse out
function clearTooltip(layout, el) {
	if (layout == 'full') {
		jQuery(el).parent().find('.tiva-event-tooltip').css('opacity', '0');
		jQuery(el).parent().find('.tiva-event-tooltip').css('-webkit-transform', 'translate3d(0,-10px,0)');
		jQuery(el).parent().find('.tiva-event-tooltip').css('transform', 'translate3d(0,-10px,0)');
	} else {
		jQuery(el).find('.tiva-event-tooltip').css('opacity', '0');
		jQuery(el).find('.tiva-event-tooltip').css('-webkit-transform', 'translate3d(0,-10px,0)');
		jQuery(el).find('.tiva-event-tooltip').css('transform', 'translate3d(0,-10px,0)');
	}
}

// Show event detail
function showEventList(layout, max_events) {
	// Sort event via upcoming
	var upcoming_events = getEventsByTime('upcoming');
	upcoming_events.sort(sortEventsByUpcoming);
	var past_events = getEventsByTime('past');
	past_events.sort(sortEventsByUpcoming);
	var tiva_list_events = upcoming_events.concat(past_events);
	tiva_list_events = tiva_list_events.slice(0, max_events);

	if (layout == 'full') {
		jQuery('.tiva-event-list-full').html('');
		for (var i = 0; i < tiva_list_events.length; i++) {
			// Start date
			var day = new Date(tiva_list_events[i].year, Number(tiva_list_events[i].month) - 1, tiva_list_events[i].day);
			if (date_start == 'sunday') {
				var event_day = wordDay[day.getDay()];
			} else {
				if (day.getDay() > 0) {
					var event_day = wordDay[day.getDay() - 1];
				} else {
					var event_day = wordDay[6];
				}
			}
			var event_date = wordMonth[Number(tiva_list_events[i].month) - 1] + ' ' + tiva_list_events[i].day + ', ' + tiva_list_events[i].year;

			// End date
			var event_end_time = '';
			if (tiva_list_events[i].duration > 1) {
				var end_date = new Date(tiva_list_events[i].year, Number(tiva_list_events[i].month) - 1, Number(tiva_list_events[i].day) + Number(tiva_list_events[i].duration) - 1);

				if (date_start == 'sunday') {
					var event_end_day = wordDay[end_date.getDay()];
				} else {
					if (end_date.getDay() > 0) {
						var event_end_day = wordDay[end_date.getDay() - 1];
					} else {
						var event_end_day = wordDay[6];
					}
				}
				var event_end_date = wordMonth[Number(end_date.getMonth())] + ' ' + end_date.getDate() + ', ' + end_date.getFullYear();
				event_end_time = ' - ' + event_end_day + ', ' + event_end_date;
			}

			// Event time
			if (tiva_list_events[i].time) {
				var event_time = '<i class="fa fa-clock-o"></i>' + tiva_list_events[i].time;
			} else {
				var event_time = '';
			}

			// Event image
			if (tiva_list_events[i].image) {
				var event_image = '<img src="' + tiva_list_events[i].image + '" alt="' + tiva_list_events[i].name + '" />';
			} else {
				var event_image = '';
			}

			// Event location
			if (tiva_list_events[i].location) {
				var event_location = '<i class="fa fa-external-link-square"></i>' + '<a href="' + tiva_list_events[i].location + '" target="_blank">' + tiva_list_events[i].location + '</a>';
			} else {
				var event_location = '';
			}

			jQuery('.tiva-event-list-full').append('<div class="event-item">'
				+ '<div class="event-item-left pull-left">'
				+ '<div class="event-image link" onclick="showEventDetail(' + tiva_list_events[i].id + ', \'full\', 0, 0, 0)">' + event_image + '</div>'
				+ '</div>'
				+ '<div class="event-item-right pull-left">'
				+ '<div class="event-name link" onclick="showEventDetail(' + tiva_list_events[i].id + ', \'full\', 0, 0, 0)">' + tiva_list_events[i].name + '</div>'
				+ '<div class="event-date"><i class="fa fa-calendar-o"></i>' + event_day + ', ' + event_date + event_end_time + '</div>'
				+ '<div class="event-time">' + event_time + '</div>'
				+ '<div class="event-location">' + event_location + '</div>'
				+ '<div class="event-intro">' + getShortText(tiva_list_events[i].description, 25) + '</div>'
				+ '</div>'
				+ '</div>'
				+ '<div class="cleardiv"></div>'
			);
		}
	} else {
		jQuery('.tiva-event-list-compact').html('');
		for (var i = 0; i < tiva_list_events.length; i++) {
			// Start date
			var day = new Date(tiva_list_events[i].year, Number(tiva_list_events[i].month) - 1, tiva_list_events[i].day);
			if (date_start == 'sunday') {
				var event_day = wordDay[day.getDay()];
			} else {
				if (day.getDay() > 0) {
					var event_day = wordDay[day.getDay() - 1];
				} else {
					var event_day = wordDay[6];
				}
			}
			var event_date = wordMonth[Number(tiva_list_events[i].month) - 1] + ' ' + tiva_list_events[i].day + ', ' + tiva_list_events[i].year;

			// End date
			var event_end_time = '';
			if (tiva_list_events[i].duration > 1) {
				var end_date = new Date(tiva_list_events[i].year, Number(tiva_list_events[i].month) - 1, Number(tiva_list_events[i].day) + Number(tiva_list_events[i].duration) - 1);

				if (date_start == 'sunday') {
					var event_end_day = wordDay[end_date.getDay()];
				} else {
					if (end_date.getDay() > 0) {
						var event_end_day = wordDay[end_date.getDay() - 1];
					} else {
						var event_end_day = wordDay[6];
					}
				}
				var event_end_date = wordMonth[Number(end_date.getMonth())] + ' ' + end_date.getDate() + ', ' + end_date.getFullYear();
				event_end_time = ' - ' + event_end_day + ', ' + event_end_date;
			}

			// Event time
			if (tiva_list_events[i].time) {
				var event_time = '<i class="fa fa-clock-o"></i>' + tiva_list_events[i].time;
			} else {
				var event_time = '';
			}

			// Event image
			if (tiva_list_events[i].image) {
				var event_image = '<img src="' + tiva_list_events[i].image + '" alt="' + tiva_list_events[i].name + '" />';
			} else {
				var event_image = '';
			}

			// Event location
			if (tiva_list_events[i].location) {
				var event_location = '<i class="fa fa-external-link-square"></i>' + '<a href="' + tiva_list_events[i].location + '" target="_blank">' + tiva_list_events[i].location + '</a>';
			} else {
				var event_location = '';
			}

			jQuery('.tiva-event-list-compact').append('<div class="event-item">'
				+ '<div class="event-image link" onclick="showEventDetail(' + tiva_list_events[i].id + ', \'compact\', 0, 0, 0)">' + event_image + '</div>'
				+ '<div class="event-name link" onclick="showEventDetail(' + tiva_list_events[i].id + ', \'compact\', 0, 0, 0)">' + tiva_list_events[i].name + '</div>'
				+ '<div class="event-date"><i class="fa fa-calendar-o"></i>' + event_day + ', ' + event_date + event_end_time + '</div>'
				+ '<div class="event-time">' + event_time + '</div>'
				+ '<div class="event-location">' + event_location + '</div>'
				+ '<div class="event-intro">' + getShortText(tiva_list_events[i].description, 15) + '</div>'
				+ '</div>'
				+ '<div class="cleardiv"></div>'
			);
		}
	}
}

// Show event detail
function showEventDetail(id, layout, day, month, year) {
	jQuery('.tiva-events-calendar.' + layout + ' .back-calendar').show();
	jQuery('.tiva-events-calendar.' + layout + ' .tiva-calendar').hide();
	jQuery('.tiva-events-calendar.' + layout + ' .tiva-event-list').hide();
	jQuery('.tiva-events-calendar.' + layout + ' .tiva-event-detail').fadeIn(1500);

	jQuery('.tiva-events-calendar.' + layout + ' .list-view').removeClass('active');
	jQuery('.tiva-events-calendar.' + layout + ' .calendar-view').removeClass('active');

	if (layout == 'full') {
		// Start date
		var day = new Date(tiva_events[id].year, Number(tiva_events[id].month) - 1, tiva_events[id].day);
		if (date_start == 'sunday') {
			var event_day = wordDay[day.getDay()];
		} else {
			if (day.getDay() > 0) {
				var event_day = wordDay[day.getDay() - 1];
			} else {
				var event_day = wordDay[6];
			}
		}
		var event_date = wordMonth[Number(tiva_events[id].month) - 1] + ' ' + tiva_events[id].day + ', ' + tiva_events[id].year;

		// End date
		var event_end_time = '';
		if (tiva_events[id].duration > 1) {
			var end_date = new Date(tiva_events[id].year, Number(tiva_events[id].month) - 1, Number(tiva_events[id].day) + Number(tiva_events[id].duration) - 1);

			if (date_start == 'sunday') {
				var event_end_day = wordDay[end_date.getDay()];
			} else {
				if (end_date.getDay() > 0) {
					var event_end_day = wordDay[end_date.getDay() - 1];
				} else {
					var event_end_day = wordDay[6];
				}
			}
			var event_end_date = wordMonth[Number(end_date.getMonth())] + ' ' + end_date.getDate() + ', ' + end_date.getFullYear();
			event_end_time = ' - ' + event_end_day + ', ' + event_end_date;
		}

		// Event time
		if (tiva_events[id].time) {
			var event_time = '<i class="fa fa-clock-o"></i>' + tiva_events[id].time;
		} else {
			var event_time = '';
		}

		// Event image
		if (tiva_events[id].image) {
			var event_image = '<img src="' + tiva_events[id].image + '" alt="' + tiva_events[id].name + '" />';
		} else {
			var event_image = '';
		}

		// Event location
		if (tiva_events[id].location) {
			var event_location = '<i class="fa fa-external-link-square"></i>' + '<a href="' + tiva_events[id].location + '" target="_blank">' + tiva_events[id].location + '</a>';
		} else {
			var event_location = '';
		}

		// Event description
		if (tiva_events[id].description) {
			var event_desc = '<div class="event-desc">' + tiva_events[id].description + '</div>';
		} else {
			var event_desc = '';
		}

		jQuery('.tiva-event-detail-full').html('<div class="event-item">'
			+ '<div class="event-image">' + event_image + '</div>'
			+ '<div class="event-name">' + tiva_events[id].name + '</div>'
			+ '<div class="event-date"><i class="fa fa-calendar-o"></i>' + event_day + ', ' + event_date + event_end_time + '</div>'
			+ '<div class="event-time">' + event_time + '</div>'
			+ '<div class="event-location">' + event_location + '</div>'
			+ event_desc
			+ '</div>'
		);
	} else {
		jQuery('.tiva-event-detail-compact').html('');
		if (day && month && year) {
			var events = getEvents(day, month, year);
		} else {
			var events = [{ id: id }];
		}
		for (var i = 0; i < events.length; i++) {
			if (typeof events[i] != "undefined") {
				// Start date
				var day = new Date(tiva_events[events[i].id].year, Number(tiva_events[events[i].id].month) - 1, tiva_events[events[i].id].day);
				if (date_start == 'sunday') {
					var event_day = wordDay[day.getDay()];
				} else {
					if (day.getDay() > 0) {
						var event_day = wordDay[day.getDay() - 1];
					} else {
						var event_day = wordDay[6];
					}
				}
				var event_date = wordMonth[Number(tiva_events[events[i].id].month) - 1] + ' ' + tiva_events[events[i].id].day + ', ' + tiva_events[events[i].id].year;

				// End date
				var event_end_time = '';
				if (tiva_events[events[i].id].duration > 1) {
					var end_date = new Date(tiva_events[events[i].id].year, Number(tiva_events[events[i].id].month) - 1, Number(tiva_events[events[i].id].day) + Number(tiva_events[events[i].id].duration) - 1);

					if (date_start == 'sunday') {
						var event_end_day = wordDay[end_date.getDay()];
					} else {
						if (end_date.getDay() > 0) {
							var event_end_day = wordDay[end_date.getDay() - 1];
						} else {
							var event_end_day = wordDay[6];
						}
					}
					var event_end_date = wordMonth[Number(end_date.getMonth())] + ' ' + end_date.getDate() + ', ' + end_date.getFullYear();
					event_end_time = ' - ' + event_end_day + ', ' + event_end_date;
				}

				// Event time
				if (tiva_events[events[i].id].time) {
					var event_time = '<i class="fa fa-clock-o"></i>' + tiva_events[events[i].id].time;
				} else {
					var event_time = '';
				}

				// Event image
				if (tiva_events[events[i].id].image) {
					var event_image = '<img src="' + tiva_events[events[i].id].image + '" alt="' + tiva_events[events[i].id].name + '" />';
				} else {
					var event_image = '';
				}

				// Event location
				if (tiva_events[events[i].id].location) {
					var event_location = '<i class="fa fa-external-link-square"></i>' + '<a href="' + tiva_events[events[i].id].location; + '" target="_blank">' + tiva_events[events[i].id].location; + '</a>';
				} else {
					var event_location = '';
				}

				// Event description
				if (tiva_events[events[i].id].description) {
					var event_desc = '<div class="event-desc">' + tiva_events[events[i].id].description + '</div>';
				} else {
					var event_desc = '';
				}

				jQuery('.tiva-event-detail-compact').append('<div class="event-item">'
					+ '<div class="event-image">' + event_image + '</div>'
					+ '<div class="event-name">' + tiva_events[events[i].id].name + '</div>'
					+ '<div class="event-date"><i class="fa fa-calendar-o"></i>' + event_day + ', ' + event_date + event_end_time + '</div>'
					+ '<div class="event-time">' + event_time + '</div>'
					+ '<div class="event-location">' + event_location + '</div>'
					+ event_desc
					+ '</div>'
				);
			}
		}
	}
}

jQuery(document).ready(function () {
	// Init calendar full
	if (jQuery('.tiva-events-calendar.full').length) {
		jQuery('.tiva-events-calendar.full').html('<div class="events-calendar-bar">'
			+ '<span class="bar-btn calendar-view active"><i class="fa fa-calendar-o"></i>' + calendar_view + '</span>'
			+ '<span class="bar-btn list-view"><i class="fa fa-list"></i>' + list_view + '</span>'
			+ '<span class="bar-btn back-calendar pull-right active"><i class="fa fa-caret-left"></i>' + back + '</span>'
			+ '</div>'
			+ '<div class="cleardiv"></div>'
			+ '<div class="tiva-events-calendar-wrap">'
			+ '<div class="tiva-calendar-full tiva-calendar"></div>'
			+ '<div class="tiva-event-list-full tiva-event-list"></div>'
			+ '<div class="tiva-event-detail-full tiva-event-detail"></div>'
			+ '</div>'
		);
	}

	// Init calendar compact
	if (jQuery('.tiva-events-calendar.compact').length) {
		jQuery('.tiva-events-calendar.compact').html('<div class="events-calendar-bar">'
			+ '<span class="bar-btn calendar-view active"><i class="fa fa-calendar-o"></i>' + calendar_view + '</span>'
			+ '<span class="bar-btn list-view"><i class="fa fa-list"></i>' + list_view + '</span>'
			+ '<span class="bar-btn back-calendar pull-right active"><i class="fa fa-caret-left"></i>' + back + '</span>'
			+ '</div>'
			+ '<div class="cleardiv"></div>'
			+ '<div class="tiva-events-calendar-wrap">'
			+ '<div class="tiva-calendar-compact tiva-calendar"></div>'
			+ '<div class="tiva-event-list-compact tiva-event-list"></div>'
			+ '<div class="tiva-event-detail-compact tiva-event-detail"></div>'
			+ '</div>'
		);
	}

	// Show - Hide view
	jQuery('.tiva-events-calendar .back-calendar').hide();
	jQuery('.tiva-event-list').hide();
	jQuery('.tiva-event-detail').hide();

	jQuery('.tiva-events-calendar').each(function (index) {
		// Hide switch button
		var switch_button = (typeof jQuery(this).attr('data-switch') != "undefined") ? jQuery(this).attr('data-switch') : 'show';
		if (switch_button == 'hide') {
			jQuery(this).find('.calendar-view').hide();
			jQuery(this).find('.list-view').hide();

			// Change css of button back
			jQuery(this).find('.events-calendar-bar').css('position', 'relative');
			jQuery(this).find('.back-calendar').css({ "position": "absolute", "margin-top": "15px", "right": "15px" });
			jQuery(this).find('.tiva-event-detail').css('padding-top', '60px');
		}
	});

	// Set wordDay
	date_start = (typeof jQuery('.tiva-events-calendar').attr('data-start') != "undefined") ? jQuery('.tiva-events-calendar').attr('data-start') : 'sunday';
	if (date_start == 'sunday') {
		wordDay = new Array(wordDay_sun, wordDay_mon, wordDay_tue, wordDay_wed, wordDay_thu, wordDay_fri, wordDay_sat);
	} else { // Start with Monday
		wordDay = new Array(wordDay_mon, wordDay_tue, wordDay_wed, wordDay_thu, wordDay_fri, wordDay_sat, wordDay_sun);
	}

	// Get events from json file or ajax php
	var source = (typeof jQuery('.tiva-events-calendar').attr('data-source') != "undefined") ? jQuery('.tiva-events-calendar').attr('data-source') : 'json';
	if (source == 'json') { // Get events from json file : events/events.json
		console.log(events_json)
		jQuery.getJSON(events_json, function (data) {
			for (var i = 0; i < data.items.length; i++) {
				var event_date = new Date(data.items[i].year, Number(data.items[i].month) - 1, data.items[i].day);
				data.items[i].date = event_date.getTime();
				tiva_events.push(data.items[i]);
			}

			// Sort events by date
			tiva_events.sort(sortEventsByDate);

			for (var j = 0; j < tiva_events.length; j++) {
				tiva_events[j].id = j;
				if (!tiva_events[j].duration) {
					tiva_events[j].duration = 1;
				}
			}

			// Create calendar
			changedate('current', 'full');
			changedate('current', 'compact');

			jQuery('.tiva-events-calendar').each(function (index) {
				// Initial view
				var initial_view = (typeof jQuery(this).attr('data-view') != "undefined") ? jQuery(this).attr('data-view') : 'calendar';
				if (initial_view == 'list') {
					jQuery(this).find('.list-view').click();
				}
			});
		});
	} else { // Get events from php file via ajax
		jQuery.ajax({
			url: events_php,
			dataType: 'json',
			data: '',
			beforeSend: function () {
				jQuery('.tiva-calendar').html('<div class="loading"><img src="assets/images/loading.gif" /></div>');
			},
			success: function (data) {
				for (var i = 0; i < data.length; i++) {
					var event_date = new Date(data[i].year, Number(data[i].month) - 1, data[i].day);
					data[i].date = event_date.getTime();
					tiva_events.push(data[i]);
				}

				// Sort events by date
				tiva_events.sort(sortEventsByDate);

				for (var j = 0; j < tiva_events.length; j++) {
					tiva_events[j].id = j;
					if (!tiva_events[j].duration) {
						tiva_events[j].duration = 1;
					}
				}

				// Create calendar
				changedate('current', 'full');
				changedate('current', 'compact');

				jQuery('.tiva-events-calendar').each(function (index) {
					// Initial view
					var initial_view = (typeof jQuery(this).attr('data-view') != "undefined") ? jQuery(this).attr('data-view') : 'calendar';
					if (initial_view == 'list') {
						jQuery(this).find('.list-view').click();
					}
				});
			}
		});
	}

	// Click - Calendar view btn
	jQuery('.tiva-events-calendar .calendar-view').click(function () {
		jQuery(this).parents('.tiva-events-calendar').find('.back-calendar').hide();
		jQuery(this).parents('.tiva-events-calendar').find('.tiva-event-list').hide();
		jQuery(this).parents('.tiva-events-calendar').find('.tiva-event-detail').hide();
		jQuery(this).parents('.tiva-events-calendar').find('.tiva-calendar').fadeIn(1500);

		jQuery(this).parents('.tiva-events-calendar').find('.list-view').removeClass('active');
		jQuery(this).parents('.tiva-events-calendar').find('.calendar-view').addClass('active');
	});

	// Click - List view btn
	jQuery('.tiva-events-calendar .list-view').click(function () {
		jQuery(this).parents('.tiva-events-calendar').find('.back-calendar').hide();
		jQuery(this).parents('.tiva-events-calendar').find('.tiva-calendar').hide();
		jQuery(this).parents('.tiva-events-calendar').find('.tiva-event-detail').hide();
		jQuery(this).parents('.tiva-events-calendar').find('.tiva-event-list').fadeIn(1500);

		jQuery(this).parents('.tiva-events-calendar').find('.calendar-view').removeClass('active');
		jQuery(this).parents('.tiva-events-calendar').find('.list-view').addClass('active');

		var layout = jQuery(this).parents('.tiva-events-calendar').attr('class') ? jQuery(this).parents('.tiva-events-calendar').attr('class') : 'full';
		var max_events = jQuery(this).parents('.tiva-events-calendar').attr('data-events') ? jQuery(this).parents('.tiva-events-calendar').attr('data-events') : 1000;
		if (layout.indexOf('full') != -1) {
			showEventList('full', max_events);
		} else {
			showEventList('compact', max_events);
		}
	});

	// Click - Back calendar btn
	jQuery('.tiva-events-calendar .back-calendar').click(function () {
		jQuery(this).parents('.tiva-events-calendar').find('.back-calendar').hide();
		jQuery(this).parents('.tiva-events-calendar').find('.tiva-event-detail').hide();

		var initial_view = (typeof jQuery(this).parents('.tiva-events-calendar').attr('data-view') != "undefined") ? jQuery(this).parents('.tiva-events-calendar').attr('data-view') : 'calendar';
		if (initial_view == 'calendar') {
			jQuery(this).parents('.tiva-events-calendar').find('.tiva-calendar').fadeIn(1500);

			jQuery(this).parents('.tiva-events-calendar').find('.list-view').removeClass('active');
			jQuery(this).parents('.tiva-events-calendar').find('.calendar-view').addClass('active');
		} else {
			jQuery(this).parents('.tiva-events-calendar').find('.tiva-event-list').fadeIn(1500);

			jQuery(this).parents('.tiva-events-calendar').find('.calendar-view').removeClass('active');
			jQuery(this).parents('.tiva-events-calendar').find('.list-view').addClass('active');
		}
	});

});
