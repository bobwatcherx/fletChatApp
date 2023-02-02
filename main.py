from flet import *
import firebase_admin
from firebase_admin import firestore,credentials
import uuid
user_id = str(uuid.uuid4())


# YOU SERVICE ACCOUNT JSON HERE LOCATION
cred =  credentials.Certificate("service_account.json")
app = firebase_admin.initialize_app(cred)


db = firestore.client()


def main(page:Page):
	page.scroll="auto"
	allmessages = Column(scroll="auto")


	def sendmessage(e):
		try:
			msg = {
			u'name':youname.value,
			u'msg':txtchat.value,
			u'id_message':user_id
			}
			res = db.collection(u"chat").add(msg)
			print(f"MESSAGE SEND SUCCESS {res}")

			# AND IF SUCCESS SEND YOU CALL PUBSUB 
			# FOR SEND YOU FRIEND ON REALTIME MESSAGE
			# LIKE WEBSOCKET
			page.pubsub.send_all(f"{youname.value}:{txtchat.value}")
			# CLEAR INPUT MESSAGE
			txtchat.value = ""
			page.update()
		except Exception as e:
			print(e)
			print("MESSAGE FAILED TO SEND")


	# NOW CREATE PUBSUB FUNCTION FOR RECEIVE MESSAGE FROM YOU FRIEND

	def on_message(msg):
		# NOW REMOVE : 
		# EXAMPLE jaja:lili
		# I WANT GET jaja value from statement above
		split_msg = msg.split(":")
		allmessages.controls.append(
			Row([
				Container(
					padding=20,
					border_radius=30,
					# THIS SCRIPT IS IF YOU SENDER THEN COLOR BLUE
					bgcolor="blue200" if split_msg[0] == youname.value else "orange200",
					content=Column([
						Text(split_msg[0]),
						Text(split_msg[1],
							size=22,
							weight="bold"
						),

						])

					)

				# NOW IF YOU SENDER THEN YOU CONTAINER ALIGN RIGHT OR RECEIVE THEN COINTAINER ALIGN LEFT

				],alignment="end" if split_msg[0] == youname.value else "start")
			)
		page.update()

	page.pubsub.subscribe(on_message)


	# NOW CREATE getmessage IF YOU FLET APP FIRST LOADED
	# THEN GET DATA FROM FIRESTORE THEN PUSH TO WIDGET
	def getmessage(e):
		allmessages.controls.clear()
		docs = db.collection(u"chat").stream()
		for x in docs:
			allmessages.controls.append(
			Row([
			Container(
				padding=20,
				border_radius=20,
				# THIS SCRIPT IS IF YOU SENDER THEN COTNAINER COLOR IS BLUE
				bgcolor="blue200" if x.to_dict()['name'] == youname.value else "orange200",
				content=Column([
						Text(f"{x.to_dict()['name']}"),
						Text(f"{x.to_dict()['msg']}",
							size=22,
							weight="bold"
						),

						])


				)

				],alignment="end" if x.to_dict()['name'] == youname.value else "start")


				)
		# NOW SET CONTAINER TEXTFIELD SEND TO SHOW AGAIN
		page_layout.visible = True
		page.update()


	# CREATE NAME OF YOU CHAT 
	youname = TextField(label="you name",
		on_submit=getmessage
		)



	# CREATE TEXTFIELD FOR CHAT MESSAGE
	txtchat = TextField(label="message",
		# REMOVE BORDER
		border = InputBorder.NONE,
		text_size=20,
		on_submit=sendmessage

		)



	# CREATE CONTAINER FOR TEXTFIELD MESSAGE AND BUTTON SEND
	chatcontianer = Container(
		bgcolor="blue",
		padding=20,
		border_radius=30,
		content=Row([
			txtchat,
			IconButton(icon="send",
			icon_size=30,
			on_click=sendmessage
			) 

			])

		)

	# NOW CREATE LAYOUT FOR ALL CHAT AND YOU TEXTFIELD MESSAGE
	page_layout = Column([
		Container(
			height=500,
			content=Column([
			allmessages,
				],scroll="auto")
			),
		chatcontianer 
		])


	# AND SET DEFAULT TEXTFIELD FOR SEND MESSAGE IS HIDE
	page_layout.visible = False

	page.add(
	Column([
	Row([
		Text("Firebase chat",size=30,
		weight="bold"
		),
		youname 
	]),
	page_layout

	])
	)


flet.app(target=main)
