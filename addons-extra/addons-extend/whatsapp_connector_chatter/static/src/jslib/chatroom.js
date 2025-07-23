odoo.define('@d68a026058b022ff11bca00cf4e8955cba72cec01425e1d73f378af00de5ae8e',async function(require){'use strict';let __exports={};const{registerMessagingComponent}=require('@mail/utils/messaging_component')
const{Conversation}=require('@0ac266676776f61364330bb041a16d836d8b315459e04c1a3381740f295958c7')
const{ConversationThread}=require('@717da89923407d2bbdeadd4f99b9e8918889493cac89cdeb293e1e42f46b02fa')
const{ConversationModel}=require('@e71c685495b3fd5a77d050fe9a0ee4564da20c118bd360ce54260886e1bb13ef')
const{Component,EventBus,useSubEnv,useState,onWillDestroy,onWillStart,useRef,onWillUpdateProps}=owl
const ChatterChatroom=__exports.ChatterChatroom=class ChatterChatroom extends Component{setup(){super.setup()
this.env;this.state=useState(this.getInitState())
this.currencyId=null
this.showUserInMessage=false
this.chatroomRef=useRef('chatroomRef')
useSubEnv(this.getSubEnv())
this.env.chatBus.on('selectConversation',this,this.selectConversation)
onWillStart(this.willStart.bind(this))
onWillUpdateProps(this.willUpdateProps.bind(this))
onWillDestroy(this.destroy.bind(this))}
getInitState(){return{selectedConversation:null,conversations:[],}}
getSubEnv(){return{context:{},chatBus:new EventBus(),chatModel:'acrux.chat.conversation',getCurrency:()=>this.currencyId,chatroomJsId:null,getShowUser:()=>this.showUserInMessage,canTranscribe:()=>false}}
async willStart(){this.currencyId=await this.getCurrency()
this.showUserInMessage=await this.env.services.user.hasGroup('whatsapp_connector.group_chat_show_user_in_message')
await this.willUpdateProps(this.props)}
async willUpdateProps(nextProps){this.state.conversations=await this.getServerConversation(nextProps)
if(this.state.conversations.length){await this.selectConversation({conv:this.state.conversations[0]})}else{this.state.selectedConversation=null}}
destroy(){this.env.chatBus.off('selectConversation',this)}
async getServerConversation(props){const{orm}=this.env.services
let data=[]
if(props.chatter.thread?.model==='acrux.chat.conversation'){if(props.chatter.thread.id){data=await orm.call(this.env.chatModel,'build_dict',[[props.chatter.thread.id],22],{context:this.env.context})}}else{const partnerId=this.chatroomPartner(props)
if(partnerId){data=await orm.call(this.env.chatModel,'search_conversation_by_partner',[partnerId,22],{context:this.env.context})}}
const out=[]
for await(const conv of data){const con=new ConversationModel(this,conv)
await con.buildExtraObj()
await con.setMessages(conv.messages)
out.push(con)}
return out}
async getCurrency(){const{orm}=this.env.services
const currency=await orm.read('res.company',[this.env.services.company.currentCompany.id],['currency_id'],{context:this.env.context})
return currency[0].currency_id[0]}
async selectConversation({conv}){this.state.selectedConversation=conv}
chatroomPartner(props){let out=null
if(props.chatter.thread?.model==='res.partner'){out=props.chatter.thread.id}else if(props.chatter.thread?.model){if(props.chatter.webRecord?.data?.partner_id){const partner=props.chatter.webRecord.data.partner_id
if(Array.isArray(partner)&&partner.length){out=partner[0]}}}
return out}}
Object.assign(ChatterChatroom,{props:{chatter:Object},components:{Conversation,ConversationThread,},template:'chatter.Chatroom',})
registerMessagingComponent(ChatterChatroom)
return __exports;});;
odoo.define('@f2486f7b74bc40dc59eb05656ef37492017e86e806215e389636cee4c42bf325',async function(require){'use strict';let __exports={};const{ChatterContainer}=require('@mail/components/chatter_container/chatter_container')
const{patch}=require('@web/core/utils/patch')
patch(ChatterContainer.prototype,'whatsapp_connector_chatter',{async _insertFromProps(props){const _super=this._super
const chatroomInChatter=await this.env.services.user.hasGroup('whatsapp_connector_chatter.group_chat_in_chatter')
return _super.apply(this,[{...props,chatroomInChatter}])}})
return __exports;});;
odoo.define('@7ad6ee0a9a19c3a337c1f13a7637c28559459d0544f5dc200f8b150bda31bf97',async function(require){'use strict';let __exports={};require('@mail/models/chatter')
const{registerPatch}=require('@mail/model/model_core')
const{attr}=require('@mail/model/model_field')
const{clear}=require('@mail/model/model_field_command')
registerPatch({name:'Chatter',recordMethods:{onClickWhatsappTalk(){if(this.isWhatsappTalkVisible){this.update({isWhatsappTalkVisible:false})}else{this.showWhatsappTalk()}},showWhatsappTalk(){this.update({composerView:clear(),isWhatsappTalkVisible:true})},showSendMessage(){this.update({isWhatsappTalkVisible:false})
this._super()},showLogNote(){this.update({isWhatsappTalkVisible:false})
this._super()},},fields:{isWhatsappTalkVisible:attr({default:false,}),isChatroomInstalled:attr({default:true,}),isInAcruxChatroom:attr({compute(){const controller=this.env.services.action.currentController
return controller?.action?.tag==='acrux.chat.conversation_tag'},}),chatroomInChatter:attr({default:false,})}})
return __exports;});;
