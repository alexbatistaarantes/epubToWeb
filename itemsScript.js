document.addEventListener('DOMContentLoaded', function(){
    loadConfigs();
});

// load parameters passed from get
function loadConfigs(){
    var parametersString = window.location.search.substr(1);
    var parameters = getParametersFromString( parametersString );
    setTheme( parameters['theme'] );
    setFontSize( parseInt( parameters['fontsize'] ) );
}

function getParametersFromString( parametersString ){
    var parameters = {theme: '', fontSize: ''};
    if(parametersString.length == 0){ return parameters; }
    var splittedParameters = parametersString.split('&');
    for( var i = 0; i < splittedParameters.length; i++){
        var parameter = splittedParameters[i].split('=')[0].toLowerCase();
        var value = splittedParameters[i].split('=')[1].toLowerCase();
        parameters[parameter] = value;
    }
    return parameters;
}

// THEME FUNCTIONS
function shiftTheme(){
    var button = document.getElementById('shiftTheme_button');
    var theme = button.value;
    setTheme( theme );
}
function setTheme( theme ){
    theme = theme.toLowerCase();
    switch( theme ){
        case 'dark':
            var bg = 'black';
            var fg = 'white';
            document.getElementById('shiftTheme_button').value = 'light';
            break;

        case 'light':
        default:
            theme = 'light';
            var bg = '';
            var fg = '';
            document.getElementById('shiftTheme_button').value = 'dark';
            break;
    }
    document.body.style.backgroundColor = bg;
    document.body.style.color = fg;

    setParametersInLink(theme);
}

// FONT FUNCTIONS
var DEFAULT_INCREASE_FONT_SIZE = 5;
function increaseFont(size = DEFAULT_INCREASE_FONT_SIZE){
    var body = document.getElementsByTagName('body')[0];
    size += parseInt(window.getComputedStyle(body)['font-size']);
    setFontSize( size );
}
function decreaseFont(size = DEFAULT_INCREASE_FONT_SIZE){ increaseFont( size * -1); }
function setFontSize( size ){
    document.body.style.fontSize = size.toString() + 'px';
    setParametersInLink(theme='', fontSize = size);
}

// SET PARAMETERS IN NAVIGATION LINKS
function setParametersInLink(theme = '', fontSize = null){
    if( theme == '' ){
        theme = (document.getElementById('shiftTheme_button').value == 'dark')
                    ? 'light' 
                    : 'dark';
    }
    if( fontSize == null ){
        fontSize = parseInt(window.getComputedStyle(document.body)['font-size']);
    }
    var urlParametersString = '?theme='+theme+"&fontSize="+String(fontSize)+"px"
    
    var navLinks = document.getElementsByClassName('navLink');
    for( var i = 0; i < navLinks.length; i++ ){
        navLinks[i].href = navLinks[i].getAttribute('value') + urlParametersString;
    }
}

// NAVIGATION FUNCTIONS
function goToBookIndex(){ document.getElementsByClassName('bookIndexLink')[0].click(); }
function goToPreviousPage(){ document.getElementsByClassName('previousPageLink')[0].click();}
function goToNextPage(){ document.getElementsByClassName('nextPageLink')[0].click(); }

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
            case 73: // i
                goToBookIndex(); break;
            case 188: // ,
                goToPreviousPage(); break;
            case 190: // .
                goToNextPage(); break;
            default: break;
        }           
    }
}

// Handle messages received from parent when used a shortcut
function handleMessage( messageObj ){
    var message = messageObj.data;
    switch( message ){
        case 'increaseFont': increaseFont(); break;
        case 'decreaseFont': decreaseFont(); break;
        case 'shiftTheme': shiftTheme(); break;
        case 'goToBookIndex': goToBookIndex(); break;
        case 'goToPreviousPage': goToPreviousPage(); break;
        case 'goToNextPage': goToNextPage(); break;
        default: break;
    }
}
window.addEventListener("message", handleMessage, false);

// Shortcuts to parent
function increaseWidth(){ parent.postMessage("+w", "*"); }
function decreaseWidth(){ parent.postMessage("-w", "*"); }
function increaseHeight(){ parent.postMessage("+h", "*"); }
function decreaseHeight(){ parent.postMessage("-h", "*"); }

function sendConsoleMessage(message){ parent.postMessage("console "+message, "*"); }
