from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import tempfile, os, inspect

def showcodeandrun(bloc):
    st.code(bloc)
    compiled_code = compile(bloc, "<string>", "exec")
    exec(compiled_code)
    st.divider()

def gencomponent(name, template="", script=""):
    def html():
        return f"""
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8" />
                    <title>{name}</title>
                    <link rel="stylesheet" href="https://unpkg.com/element-ui/lib/theme-chalk/index.css">
                    <script>
                        function sendMessageToStreamlitClient(type, data) {{
                            const outData = Object.assign({{
                                isStreamlitMessage: true,
                                type: type,
                            }}, data);
                            window.parent.postMessage(outData, "*");
                        }}

                        const Streamlit = {{
                            setComponentReady: function() {{
                                sendMessageToStreamlitClient("streamlit:componentReady", {{apiVersion: 1}});
                            }},
                            setFrameHeight: function(height) {{
                                sendMessageToStreamlitClient("streamlit:setFrameHeight", {{height: height}});
                            }},
                            setComponentValue: function(value) {{
                                sendMessageToStreamlitClient("streamlit:setComponentValue", {{value: value}});
                            }},
                            RENDER_EVENT: "streamlit:render",
                            events: {{
                                addEventListener: function(type, callback) {{
                                    window.addEventListener("message", function(event) {{
                                        if (event.data.type === type) {{
                                            event.detail = event.data
                                            callback(event);
                                        }}
                                    }});
                                }}
                            }}
                        }}
                    </script>

                </head>
            <body>
            {template}
            </body>
            <script src="https://unpkg.com/vue@2/dist/vue.js"></script>
            <script src="https://unpkg.com/element-ui/lib/index.js"></script>
            <script>
                {script}
            </script>
            </html>
        """

    dir = f"{tempfile.gettempdir()}/{name}"
    if not os.path.isdir(dir): os.mkdir(dir)
    fname = f'{dir}/index.html'
    f = open(fname, 'w')
    f.write(html())
    f.close()
    func = components.declare_component(name, path=str(dir))
    def f(**params):
        component_value = func(**params)
        return component_value
    return f

st.subheader('Streamlit components and when they are reinstantiated', divider='rainbow')
st.markdown("I had written an initial article (Streamlit application) showing a simplified way of creating new components in Streamlit (https://appcreatecomponent-ngm4rrw7ryvtzb6nigbbmw.streamlit.app/)")
st.markdown("In this new article, I want to showcase the side effects associated with using external components and when to reinstantiate them.")
st.markdown("I will be using 2 extremely simple components that I have defined:")
st.markdown("a) a button")
st.markdown("b) a component that has no graphical interest but echoes the initialization parameters of a component")
st.markdown("###### Button definition:")
showcodeandrun('''
template="""
    <div id="app">
        <el-button id="tobechanged" type="primary" @click="getValue">Create</el-button>
    </div>
"""
script = """
    function setText(id, newvalue) {
        var s = document.getElementById(id);
        s.innerHTML = newvalue;
    }
    function onRender(event) {
        if (!window.rendered) {
            setText('tobechanged',event.detail.args.label);
            Streamlit.setFrameHeight(document.body.scrollHeight + 20)
            window.rendered = true
        }
    }
    Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)
    Streamlit.setComponentReady()
    const vue = new Vue({
        methods: {
            getValue (event) {
                Streamlit.setComponentValue(true)
            }
        },
    }).$mount('#app')
"""

button = gencomponent('Button',template=template, script=script)
''')
template="""
    <div id="app">
        <el-button id="tobechanged" type="primary" @click="getValue">Create</el-button>
    </div>
"""
script = """
    function setText(id, newvalue) {
        var s = document.getElementById(id);
        s.innerHTML = newvalue;
    }
    function onRender(event) {
        if (!window.rendered) {
            setText('tobechanged',event.detail.args.label);
            Streamlit.setFrameHeight(document.body.scrollHeight + 20)
            window.rendered = true
        }
    }
    Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)
    Streamlit.setComponentReady()
    const vue = new Vue({
        methods: {
            getValue (event) {
                Streamlit.setComponentValue(true)
            }
        },
    }).$mount('#app')
"""
button = gencomponent('FirstButton',template=template, script=script)

st.markdown("###### Echo definition:")
showcodeandrun('''
template="""
<div id="app">
</div>
"""
script = """
    function onRender(event) {
        if (!window.rendered) {
            Streamlit.setComponentValue(event.detail.args)
            Streamlit.setFrameHeight(document.body.scrollHeight)
            window.rendered = true
        }
    }
    Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)
    Streamlit.setComponentReady()
"""
echo = gencomponent('Echo',template=template, script=script)
''')

template="""
<div id="app">
</div>
"""
script = """
    function onRender(event) {
        if (!window.rendered) {
            Streamlit.setComponentValue(event.detail.args)
            Streamlit.setFrameHeight(document.body.scrollHeight)
            window.rendered = true
        }
    }
    Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)
    Streamlit.setComponentReady()
"""
echo = gencomponent('Echo',template=template, script=script)
st.markdown("An example of using the button:")
showcodeandrun('''
b1 = button(label="My button", default=False)
st.write(b1)
''')

st.markdown("Now let's compare these two programs:")
st.markdown("###### Program 1 ")
showcodeandrun('''
col1, col2 = st.columns([1,1])
with col1:
    b1 = st.button('Button1')
with col2:
    b2 = st.button('Button2')
st.write(f'b1: {b1}, b2: {b2}')
''')

st.markdown("###### Program 2 ")
showcodeandrun('''
col1, col2 = st.columns([1,1])
with col1:
    b1 = button(label='Custom button 1', default=False)
with col2:
    b2 = button(label='Custom button 2', default=False)
st.write(f'b1: {b1}, b2: {b2}')
''')
st.markdown("Can you see the difference in behavior between these two programs? Yes, of course: in program 1 which uses the standard Streamlit button, the behavior is normal; one button renders true while the other renders false, whereas in program 2, a button that has been used always renders true...")
st.markdown("Is it because the external component embodying the button is poorly programmed? **The answer is NO**, it is solely related to the behavior of Streamlit in the presence of external components.")
st.markdown("The logic of Streamlit regarding component reinitialization depends on:")
st.markdown("a) the use of the 'key' keyword in the component parameter definition")
st.markdown("b) the values of the parameters passed during the creation of the component and the values of the parameters during a re-call")
st.markdown("Let's take examples to understand the differences with the 'echo' component.")
st.markdown("###### Program 3")
showcodeandrun('''
if 'alpha' not in st.session_state: st.session_state.alpha= 0
if 'beta' not in st.session_state: st.session_state.beta = 0
col1, col2, col3  = st.columns([1,1,1])
with col1:
    value = echo(alpha=st.session_state['alpha'], beta=st.session_state['beta'])
    st.write(value)
with col2:
    b1 = st.button('Increment alpha')
with col3:
    b2 = st.button('Increment beta')
if b1: 
    st.session_state.alpha = st.session_state.alpha + 1
if b2: 
    st.session_state.beta = st.session_state.beta + 1
''')
st.markdown("Did you notice this other side effect? Take a close look... By clicking on a button, you have to wait for the next click (on the same button or another) to get the expected result.")
st.markdown("To achieve the desired result, you need to introduce the st.rerun() instruction at the right place:")
st.markdown("###### Program 4")
showcodeandrun('''
if 'gamma' not in st.session_state: st.session_state.gamma = 0
if 'delta' not in st.session_state: st.session_state.delta = 0
col1, col2, col3  = st.columns([1,1, 1])
with col1:
    value = echo(gamma=st.session_state.gamma, delta=st.session_state.delta)
    st.write(value)
with col2:
    b1 = st.button('Increment gamma')
with col3:
    b2 = st.button('Increment delta')
if b1: 
    st.session_state.gamma = st.session_state.gamma + 1
    st.rerun()
if b2: 
    st.session_state.delta = st.session_state.delta + 1
    st.rerun()
''')
st.markdown("Now let's introduce the keyword 'key' into our programs and observe Streamlit's behavior.")
st.markdown("###### Program 5")
showcodeandrun('''
if 'kalpha' not in st.session_state: st.session_state.kalpha= 0
if 'kbeta' not in st.session_state: st.session_state.kbeta = 0
col1, col2, col3  = st.columns([1,1,1])
with col1:
    value = echo(kalpha=st.session_state['kalpha'], kbeta=st.session_state['kbeta'], key="xxx")
    st.write(value)
with col2:
    b1 = st.button('Increment kalpha')
with col3:
    b2 = st.button('Increment kbeta')
if b1: 
    st.session_state.kalpha = st.session_state.kalpha + 1
if b2: 
    st.session_state.kbeta = st.session_state.kbeta + 1
''')
st.markdown("This time, the component is never reinstantiated. Its parameters change in value, but its key remains constant, and the component is never recalled by Streamlit.")
st.markdown("To make it work, the key needs to change with each interaction with the user.")
st.markdown("###### Program 6")
showcodeandrun('''
if 'kgamma' not in st.session_state: st.session_state.kgamma= 0
if 'kdelta' not in st.session_state: st.session_state.kdelta = 0
col1, col2, col3  = st.columns([1,1,1])
with col1:
    value = echo(kgamma=st.session_state['kgamma'], kdelta=st.session_state['kdelta'], key="xxx"+str(st.session_state.kgamma+st.session_state.kdelta))
    st.write(value)
with col2:
    b1 = st.button('Increment kgamma')
with col3:
    b2 = st.button('Increment kdelta')
if b1: 
    st.session_state.kgamma = st.session_state.kgamma + 1
    st.rerun()
if b2: 
    st.session_state.kdelta = st.session_state.kdelta + 1
    st.rerun()
''')

st.markdown("Now if we come back to the side effects of program 2")
st.markdown("The implementation of the external component 'button' is correct from a programming logic perspective. However, it is not suitable for dealing with Streamlit side effects. A boolean value is not sufficient to handle the various scenarios regarding the possible states of the component. It is necessary to implement at least a counter such that when the counter is incremented, the component is reset.")
st.markdown("One solution for this problem is the following:")
st.markdown("###### New button definition:")
showcodeandrun('''
template="""
    <div id="app">
        <el-button id="tobechanged" type="primary" @click="getValue">Create</el-button>
    </div>
"""
script = """
    var counter;
    function setText(id, newvalue) {
        var s = document.getElementById(id);
        s.innerHTML = newvalue;
    }
    function onRender(event) {
        if (!window.rendered) {
            setText('tobechanged',event.detail.args.label);
            counter = event.detail.args.counter;
            Streamlit.setFrameHeight(document.body.scrollHeight + 20)
            window.rendered = true
        }
    }
    Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)
    Streamlit.setComponentReady()
    const vue = new Vue({
        methods: {
            getValue (event) {
                Streamlit.setComponentValue(counter+1);
            }
        },
    }).$mount('#app')
"""
newbutton = gencomponent('NewButton',template=template, script=script)
''')

template="""
    <div id="app">
        <el-button id="tobechanged" type="primary" @click="getValue">Create</el-button>
    </div>
"""
script = """
    var counter;
    function setText(id, newvalue) {
        var s = document.getElementById(id);
        s.innerHTML = newvalue;
    }
    function onRender(event) {
        if (!window.rendered) {
            setText('tobechanged',event.detail.args.label);
            counter = event.detail.args.counter;
            Streamlit.setFrameHeight(document.body.scrollHeight + 20)
            window.rendered = true
        }
    }
    Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)
    Streamlit.setComponentReady()
    const vue = new Vue({
        methods: {
            getValue (event) {
                Streamlit.setComponentValue(counter+1);
            }
        },
    }).$mount('#app')
"""
newbutton = gencomponent('NewButton',template=template, script=script)
st.markdown("With this new definition, the following program reacts correctly to button interactions:")
st.markdown("###### Program 7")
showcodeandrun('''
if 'db1' not in st.session_state: st.session_state.db1 = 0
if 'db2' not in st.session_state: st.session_state.db2 = 0
if 'lb1' not in st.session_state: st.session_state.lb1 = 0
if 'lb2' not in st.session_state: st.session_state.lb2 = 0
col1, col2 = st.columns([1,1])
with col1:
    counter = st.session_state.db1
    b1 = newbutton(label='Custom button 1', counter=counter, default=counter)
with col2:
    counter = st.session_state.db2
    b2 = newbutton(label='Custom button 2', counter=counter, default=counter)
if b1 != st.session_state.db1:
    st.session_state.db1 = b1
    st.session_state.rb1 = True
    st.rerun()
if b2 != st.session_state.db2:
    st.session_state.db2 = b2
    st.session_state.rb2 = True
    st.rerun()
if st.session_state.db1 != st.session_state.lb1:
    rb1 = True
    st.session_state.lb1 = st.session_state.db1
else: rb1 = False
if st.session_state.db2 != st.session_state.lb2:
    rb2 = True
    st.session_state.lb2 = st.session_state.db2
else: rb2 = False
with col1:
    st.write('rb1', rb1)
with col2:
    st.write('rb2', rb2)
''')
st.markdown("If you find a simpler implementation that achieves this result, I'm interested in your solution. But have you noticed the difficulty in achieving this result? This is solely related to Streamlit's behavior when it reinstantiates components...")
st.markdown("Component developers need to be aware of Streamlit's reinstantiation mechanisms, which cause issues when using external components. Delivering a component such as 'newbutton' without encapsulating its usage is not acceptable! The end-user should focus on their application logic and not have to worry about the side effects of the components they use. At the very least, a Python class should be provided to encapsulate this 'newbutton'. For example:")
st.markdown("##### Final Program")
showcodeandrun('''
class CustomButton:
    def __init__(self, label, id=None):
        self.id = id
        self.id2 = 'xx'+id
        if self.id not in st.session_state: st.session_state[self.id] = 0
        if self.id2 not in st.session_state: st.session_state[self.id2] = 0
        b = newbutton(label=label, counter=st.session_state[self.id], id=self.id, default=st.session_state[self.id])
        if b != st.session_state[self.id]:
            st.session_state[self.id] = b
            st.rerun()
        if st.session_state[self.id] != st.session_state[self.id2]:
            self.result = True
            st.session_state[self.id2] = st.session_state[self.id]
        else: self.result = False
    def get_result(self):
        return self.result
               

col1, col2 = st.columns([1,1])
with col1:
    b1 = CustomButton('Custom button 1', id='aaazzz')
    st.write(b1.get_result())
with col2:
    b2 = CustomButton('Custom button 2', id='bbbzzz')
    st.write(b2.get_result())
''')
st.markdown("The program's behavior is now correct, and the complexity of the infrastructure has been hidden within a class.")