var ChatExtractor = class ChatExtractor{

    static observer;
    static chatDatas = [];
    static ids = {};
    constructor(){
        console.log("initializing chat extractor");
        if (this.observer){
            this.observer.disconnect();
        }
        this.chatDatas = [];
        this.ids = {};
        this.addObserver();
        this.reinit();
    }

    reinit(){
        this.postMessage("sarah", "init");
    }

    addObserver(){
        this.observer = new MutationObserver((function(mutations) {
            mutations.forEach((function(mutation) {
                if (mutation.addedNodes && mutation.addedNodes.length > 0){
                    var node = mutation.addedNodes[0];
                    var chatData = {
                        senderName: undefined,
                        message: undefined,
                        id: undefined
                    };
                    if (node.classList.contains("chat-item__chat-info")){
                        chatData.senderName = node.querySelector(".chat-item__sender")?.innerText;
                    }
                    node = node.querySelector(".chat-message-text");
                    if (node?.classList?.contains("chat-message-text") && 
                        node?.classList?.contains("chat-message-text-others")){
                        
                        
                        chatData.message = node.innerText;
                        chatData.id = node.childNodes[0].id;
                        
                        if (!chatData.senderName && this.chatDatas?.length > 0){
                            chatData.senderName = this.chatDatas[this.chatDatas.length-1].senderName;
                        }
                    }

                    if (chatData.message && !(chatData.id in this.ids)){
                        this.ids[chatData.id]= true;
                        this.chatDatas.push(chatData);
                        this.nodeAdded(chatData);
                    }
                }
            }).bind(this));
        }).bind(this));
    
        var config = {
            attributes: true,
            childList: true,
            characterData: true,
            subtree: true
        };
    
        var chatWindow = $(".chat-container__chat-list");
        this.observer.observe(chatWindow, config);
    }

    destroy(){
        this.observer?.disconnect();
    }

    nodeAdded(chatData){
        console.log("I found another message in the chat!")
        console.log(chatData.message);
        this.postMessage(chatData.senderName, chatData.message);
    }

    postMessage(name, message){
        fetch("http://localhost:5000/wereword", {
            method: "POST",
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                name: name,
                message: message
            })
        }).then((res => {
            res.json().then(realRes => {
                this.handleResponse(realRes);
            }).bind(this);
        }).bind(this));
    }

    handleResponse(res){
        console.log(res);
        if (res.log){
            this.typeMessage(res.text);
        }
    }

    typeMessage(message){
        const textarea = document.querySelector('.chat-box__chat-textarea.window-content-bottom')

        var nativeTextAreaValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
        nativeTextAreaValueSetter.call(textarea, message);

        const event = new Event('input', { bubbles: true});
        textarea.dispatchEvent(event);

        const ke = new KeyboardEvent('keydown', {
            bubbles: true, cancelable: true, keyCode: 13//or 14?
        })
        
        textarea.dispatchEvent(ke);
    }
}

var extractor = new ChatExtractor();
