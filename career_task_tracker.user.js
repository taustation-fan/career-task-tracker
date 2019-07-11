// ==UserScript==
// @name         career_task_tracker
// @version      1.0
// @author       Moritz Lenz <moritz.lenz@gmail.com>
// @description  Submit current career task rewards to a central collector. Please get an access token from moritz and add it in your preferences page.
// @match        https://alpha.taustation.space/career
// @match        https://alpha.taustation.space/career/*
// @match        https://alpha.taustation.space/preferences
// @require      https://code.jquery.com/jquery-3.3.1.min.js
// @require      https://rawgit.com/taustation-fan/userscripts/master/userscript-preferences.js
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    function status_message(message) {
        $('p#ctt_msg').remove();
        $('div.career-task-container').after('<p id="ctt_msg">Career task tracker: ' + message + '</p>')
    }

    function pref_specs() {
        return {
            key: 'career_tracker',
            label: 'Career Task Tracker',
            options: [
                {
                    key: 'token',
                    label: 'Access Token',
                    type: 'text',
                    default: '',
                }
            ],
        };
    }

    let options = userscript_preferences( pref_specs() );

    if ( !window.location.pathname.match('^/career') ) {
        return;
    }
    var token = options.token;
    if (!token) {
        status_message('Please configure your access token in the user preferences');
        return;
    }

    var station = $('span.station').text().trim();
    var career_chunks = $('div#employment_panel').find('li:Contains("Career")').find('a').text().trim().split(' - ');
    var career = career_chunks[0];
    var rank = career_chunks[1];

    var tasks = {};
    $('.table-career-tasks').each(function(table_idx) {
        $(this).find('tr').each(function() {
            var $row = $( this );
            var name = $row.find('td').eq(0).text();
            if (!name) return;
            var amount = $row.find('.currency-amount').text();
            tasks[name] = amount;
        });
    });
    if ($.isEmptyObject(tasks)) {
        status_message('No career tasks found');
        return;
    }

    var payload = {
        token: token,
        station: station,
        career: career,
        rank: rank,
        tasks: tasks,
    };

    let url = 'https://ctt.tauguide.de/v1/add';

    $.ajax({
        type: "POST",
        url: url,
        dataType: 'json',
        data: JSON.stringify(payload),
        success: function(response) {
            if (response.recorded) {
                status_message('tasks successfully recorded. +1 brownie point!');
            }
            else {
                status_message('error recording tasks: ' + response.message);
            }
        },
        error: function(xhr) {
            status_message('cannot talk to ' + url + ': ' + xhr.response_text);
        },
    });
}());
