css = '''
<style>
.chat-message {
    padding: 1.5rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    display: flex;
}

.chat-message.user {
    background-color: #1e1e1e; /* Dark gray for user messages*/
}

.chat-message.bot {
    background-color: #333333; /* Slightly lighter gray for bot messages */
}

.chat-message .avatar {
    width: 20%;
}

.chat-message .avatar img {
    max-width: 78px;
    max-height: 78px;
    border-radius: 50%;
    object-fit: cover;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.5); /* Subtle shadow around avatar */
}

.chat-message .message {
    width: 80%;
    padding: 0 1.5rem;
    color: #e0e0e0; /* Light gray for message text */
    font-size: 1rem;
    line-height: 1.5;
}

</style>
'''
bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://img.freepik.com/free-vector/graident-ai-robot-vectorart_78370-4114.jpg?t=st=1730142660~exp=1730146260~hmac=2aa632aff973883ceb364879e002b3d279586e15f71db3f10f5cc509c9a1c560&w=740" style="max-height: 80px; max-width: 80px;">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://i.ibb.co/SthNWZJ/baasha.jpg" style="max-height: 80px; max-width: 80px;">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''

