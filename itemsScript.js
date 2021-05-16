var DEFAULT_INCREASE_FONT_SIZE = 5;

function shiftTheme(){
    var button = document.getElementById('shiftTheme_button');
    switch( button.value ){
        case 'dark':
            var bg = 'black';
            var fg = 'white';
            button.value = 'light';
            break;
         case 'light':
            var bg = '';
            var fg = '';
            button.value = 'dark';
            break;
    }
    document.body.style.backgroundColor = bg;
    document.body.style.color = fg;
}
function increaseFont(size = DEFAULT_INCREASE_FONT_SIZE){
    var body = document.getElementsByTagName('body')[0];
    size += parseInt(window.getComputedStyle(body)['font-size']);
    body.style.fontSize = size.toString() + 'px';
}
function decreaseFont(size = DEFAULT_INCREASE_FONT_SIZE){ increaseFont( size * -1); }

function increaseWidth(){ parent.postMessage("+w", "*"); }
function decreaseWidth(){ parent.postMessage("-w", "*"); }
function increaseHeight(){ parent.postMessage("+h", "*"); }
function decreaseHeight(){ parent.postMessage("-h", "*"); }

// Handle shortcuts
// e.which is used instead of e.key so letters capitalized or not can be used
document.onkeydown = function(e){
    if( e.ctrlKey && e.altKey ){ // CTRL + ALT +
        switch( e.which ){
            case 87: // w
                increaseWidth(); break;
            case 72: // h
                increaseHeight(); break;
            default: break;
        }
    }else if( !e.ctrlKey && !e.altKey ){ //
        switch( e.which ){
            case 87: // w
                decreaseWidth(); break;
            case 72: // h
                decreaseHeight(); break;
            case 70: // f
                decreaseFont(); break;
            case 71: // g
                increaseFont(); break;
            case 84: // t
                shiftTheme(); break;
            default: break;
        }           
    }
}

function handleMessage( messageObj ){
    var message = messageObj.data;
    switch( message ){
        case 'increaseFont': increaseFont(); break;
        case 'decreaseFont': decreaseFont(); break;
        case 'shiftTheme': shiftTheme(); break;
        default: break;
    }
}
window.addEventListener("message", handleMessage, false);
