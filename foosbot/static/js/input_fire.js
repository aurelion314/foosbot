
handler_url = '/' + account_id + '/handler'
audio_base_url = '/static/audio/'
audio_url = audio_base_url + account_id + '.mp3'

data = {
  account_name: '',  
  session_wakeup: 60,
  message: 'Waiting',
  winner: '',
  points_won: '',
  match_data: {
    status: '',
    timeout: -1,
    player1: '',
    player2: '',
    player1_rank: '',
    player2_rank: '',
    player1_games: 0,
    player2_games: 0,
    updated_at: '',
  },
  match_history: [
  ],
  leaderboard_data: [
  ]
    // {rank:1, fname: 'Player1', elo: 1501, photo: 'http://127.0.0.1:8000/static/img/user.jpeg'},
}

// The object is added to a Vue instance
var vm_status = new
  Vue({
    el: '#input_app',
    delimiters: ['[[', ']]'],
    data: data
  })




$(document).ready(function () {
  timer()

  function timer() {
    if (data.match_data.timeout == 0) { timeout(); data.match_data.timeout = -1; }
    if (data.match_data.timeout > 0) { data.match_data.timeout = data.match_data.timeout - 1 }

    if (data.session_wakeup < 1) {
      wakeup()
    }
    data.session_wakeup -= 1
    setTimeout(timer, 1000)
  }

  function wakeup() {
    data.session_wakeup = 60
    $.post(handler_url, { 'action': 'ping' }, function (response) {
      response = JSON.parse(response)
      if (response.result == 'reload') {
        location.reload();
      }
      return (false);
    });
  }

  function processResponse(response) {
    response = JSON.parse(response)

    if (response.status == 'not found') {
      data.message = 'Player not found!'
      playAudio('Player not found!')
      return;
    }

    var date = new Date()
    var player = response['result'];
    if (player['id'] == '') { data.message = 'Player not found'; return (false); }

    //is player1 empty?
    if (data.match_data.player1 == '') {
      //update player 1, set updated_at
      if (data.match_data.timeout < 6) { data.match_data.timeout = 6 }
      data.match_data.player1 = player['id']
      data.match_data.player1_games = player['games_today']
      data.match_data.player1_rank = player['points']
      data.match_data.player1_name = player['name']
      data.match_data.status = player['name'] + ' vs  ..'
      data.message = 'Player 1 set. Waiting for player 2'
      data.match_data.updated_at = date
      showHeader('players')
      if (data.match_data.timeout < 15) { data.match_data.timeout = 15 }
      return true
    }
    //is player1 == player? voice an error 
    if (data.match_data.player1 == player['id'] && data.match_data.player2 == '') {
      data.message = 'Need new Player';
      return false;
    }

    //player1 full, player2 empty?
    if (data.match_data.player2 == '') {
      // create match, set player2, set updated at, play audio, set status = in_progress, update slack
      var postval = {}
      postval.action = 'start';
      postval.player1 = data.match_data.player1;
      postval.player2 = player['id'];
      $.post(handler_url, postval, function () {
        data.match_data.player2 = player['id']
        data.match_data.player2_games = player['games_today']
        data.match_data.player2_rank = player['points']
        data.match_data.player2_name = player['name']
        data.match_data.status = data.match_data.player1_name + ' vs ' + data.match_data.player2_name
        data.message = 'Match started';
        data.match_data.updated_at = date //.toISOString().substring(0, 10) + '  ' + date.toISOString().substring(11, 19)

        var serving;
        if (parseInt(data.match_data.player1_rank) > parseInt(player['points'])) {
          serving = player['name'];
        } else {
          serving = data.match_data.player1_name;
        }

        playAudio('' + data.match_data.player1_name + ' versus ' + data.match_data.player2_name + ', ' + serving + ' serves.')
        updateSlack('Match Started! ' + data.match_data.player1_name + ' versus ' + data.match_data.player2_name + '.')
        if (data.match_data.timeout < 1000) { data.match_data.timeout = 1000 }

        return true;
      });
      return false;
    }

    //player1 full, player 2 full. Check new player is one of these 2, more than 15 seconds has elapsed
    if (player['id'] != data.match_data.player1 && player['id'] != data.match_data.player2) {
      clearPlayers();
      data.message = 'Player not playing. Match reset'
      clearMatch();
      playAudio('Player not in current match. Match Cleared.')
      updateSlack('Match Cleared.')
      return (false);
    }
    if ((date - new Date(data.match_data.updated_at)) < 10000) {
      data.message = 'Game must last 15 seconds';
      playAudio('Match too brief')
      if (data.match_data.timeout < 1000) { data.match_data.timeout = 1000 }
      return (false);
    }

    //update game with winner, reset player1/player2, set updated_at, set status waiting for input, update slack
    var postval = {}
    postval.action = 'end';
    postval.mode = data.match_data.mode
    postval.player1 = data.match_data.player1;
    postval.player2 = data.match_data.player2;
    postval.winner = player['id'];
    loser = (player['id'] == postval.player1) ? postval.player2 : postval.player1;
    $.post(handler_url, postval, function (response) {
      response = JSON.parse(response)
      if (response.status != 'success') {
        data.message = 'Match completion failed: ' + response.status;
        clearPlayers()
        return;
      }
      var epicFollowup = ''
      var slackMessage = player['name'] + ' was Victorious!'
      clearPlayers();
      data.match_data.winner = player['name']
      data.match_data.points_won = response.points
      showHeader('winner')
      data.match_data.status = player['name'] + ' Won '+response.points+' Points!'
      data.message = 'Match complete'
      data.match_data.updated_at = date
      if (response['streak'] > 2) { epicFollowup = 'rampage'; slackMessage = player['name'] + ' is on a Rampage!'; }
      if (response['streak'] > 3) { epicFollowup = 'dominating'; slackMessage = player['name'] + ' is Dominating!' }
      if (response['streak'] > 4) { epicFollowup = 'unstoppable'; slackMessage = player['name'] + ' is Unstoppable!' }
      if (response['streak'] > 1) { slackMessage += " That's " + response['streak'] + " wins in a row!" }
      slackMessage += ' (' + (parseInt(player['wins_today']) + 1) + ' out of ' + (parseInt(player['games_today']) + 1) + ' today)'
      playAudio('' + player['name'] + ' Wins!', epicFollowup)
      updateSlack(slackMessage)
      refreshLeaderboard()
      return true;
    });
  }

  function clearMatch() {
    postval = {}
    postval.action = 'remove';
    $.post(handler_url, postval, function () {
      return true;
    });
  }

  function playAudio(data, followup = '') {
    var postval = {}
    postval.action = 'say';
    postval.words = data;
    $.post(handler_url, postval, function (response) {
      response = JSON.parse(response)
      if (response['status'] == 'success'){
        audio = new Audio(audio_url);
        $(audio).on( "ended", function(){
          if (followup != ''){
              var audio2 = new Audio(audio_base_url+followup+'.wav')
              audio2.play();
              return true
          }
          return false
        });
        audio.play();
      }else if (followup != ''){
        var audio = new Audio(audio_base_url+followup+'.wav')
        audio.play();
      }
      return true;
    });
    return false;
  }

  function clearPlayers() {
    data.match_data.player1 = ''
    data.match_data.player2 = ''
    data.match_data.player1_games = 0
    data.match_data.player2_games = 0
    data.match_data.player1_rank = ''
    data.match_data.player2_rank = ''
    data.match_data.player1_name = ''
    data.match_data.player2_name = ''
    data.match_data.timeout = -1
    data.match_data.status = ''
    data.match_data.mode = 'SINGLES MODE'
    showHeader('free')
  }

  function showHeader(mode) {
    if (!['players', 'winner', 'free'].includes(mode)){
      return false
    }
    hideAllHeaders()
    if (mode == 'players'){
      $('#table_players').show()
    }
    if (mode == 'free'){
      $('#table_free').show()
    }
    if (mode == 'winner'){
      $('#table_winner').show()
      data.match_data.timeout = 10
    }
  }

  function hideAllHeaders() {
    $('#table_players').hide()
    $('#table_winner').hide()
    $('#table_free').hide()
  }

  function updateSlack(data) {
    return;//This is no longer needed. Handled on back end
    var postval = {}
    postval.action = 'slack';
    postval.message = data;
    $.post(handler_url, postval, function () {
      return true;
    });
    return false;
  }

  function timeout() {
    //If nothing has happened, ignore timeout
    if (data.match_data.player1 == '' && data.match_data.player2 == '') { 
      showHeader('free')
      return false 
    }

    //If only player1 is entered, reset
    if (data.match_data.player2 == '') {
      clearPlayers();
      data.match_data.status = ''
      data.message = 'Timeout'
      playAudio('Timeout waiting for player 2.')
      return false
    }

    //If player1 and player 2 entered, reset and clear game from server
    clearPlayers();
    data.message = 'Timeout'
    playAudio('Time limit reached. Match cleared.')
    postval = {}
    postval.action = 'remove';
    $.post(handler_url, postval, function () {
      return true;
    });
    return false

  }

  $('#input').focus();

  $('form').submit(function (e) {
    e.preventDefault()
    input = $('#input').val()
    postval = {}
    postval.action = 'rfid'
    postval.mode = data.match_data.mode
    postval.rfid = input
    $.post(handler_url, postval, function (response) {
      processResponse(response);
      return true;
    });
    $('#input').val('');

    return false;

  });

  function refreshLeaderboard(){
    postval = {action: 'leaderboard'}
    $.post(handler_url, postval, function (response) {
      response = JSON.parse(response)
      if (response.leaderboard_data){
        data.leaderboard_data = response.leaderboard_data
      }
      if (response.match_history){
        data.match_history = response.match_history
      }
    });
  }

  refreshLeaderboard()

});