#--------------------------------------------------------------------------------------------------------------------
#               Interactive message for scheduler
#--------------------------------------------------------------------------------------------------------------------

news_scheduler_blocks = [
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "Please choose how frequently (every 1/7/14/30 days) you'd like to receive news updates (News will be posted at 9am)."
			}
		},
		{
			"type": "actions",
			"elements": [
                {
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "1 Days"
					},
					"style": "primary",
					"value": "1",
                    "action_id": "1d"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "7 Days"
					},
					"style": "primary",
					"value": "7",
                    "action_id": "7d"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "14 Days"
					},
					"style": "primary",
					"value": "14",
                    "action_id": "14d"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "30 Days"
					},
					"style": "primary",
					"value": "30",
                    "action_id": "30d"
				}
			]
		}
	]


#--------------------------------------------------------------------------------------------------------------------
#               Interactive message for category and schedule
#--------------------------------------------------------------------------------------------------------------------

news_sched_category_blocks = [
		{
			"type": "input",
			"element": {
				"type": "radio_buttons",
				"initial_option": {
					"value": "1",
					"text": {
						"type": "plain_text",
						"text": "1 Days"
					}
				},
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "1 Days"
						},
						"value": "1"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "7 Days"
						},
						"value": "7"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "14 Days"
						},
						"value": "14"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "30 Days"
						},
						"value": "30"
					}
				],
				"action_id": "radio_buttons-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Please choose how frequently (every 1/7/14/30 days) you'd like to receive news updates (News will be posted at 9am)."
			}
		},
		{
			"type": "input",
			"element": {
				"type": "checkboxes",
				"initial_options": [
					{
						"text": {
							"type": "plain_text",
							"text": "All"
						},
						"value": "All"
					}
				],
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "All"
						},
						"value": "All"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "General"
						},
						"value": "General"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Cloud Computing & Infrastructure"
						},
						"value": "Cloud Computing & Infrastructure"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Consumer Technology"
						},
						"value": "Consumer Technology"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Cyber Security & Privacy"
						},
						"value": "Cyber Security & Privacy"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Data Science & AI"
						},
						"value": "Data Science & AI"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Decentralised Computing"
						},
						"value": "Decentralised Computing"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Digital Transformation"
						},
						"value": "Digital Transformation"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "IT & Network Infrastructure"
						},
						"value": "IT & Network Infrastructure"
					}
				],
				"action_id": "checkboxes-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Please select the news category you want to see."
			}
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Submit"
					},
					"value": "schedule_category_select",
					"action_id": "schedule_category_select"
				}
			]
		}
	]

#--------------------------------------------------------------------------------------------------------------------
#               Interactive message for category
#--------------------------------------------------------------------------------------------------------------------

news_category_blocks = [
		{
			"type": "input",
			"element": {
				"type": "checkboxes",
                "initial_options": [
					{
						"text": {
							"type": "plain_text",
							"text": "All"
						},
						"value": "All"
					}
                ],
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "All"
						},
						"value": "All"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "General"
						},
						"value": "General"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Cloud Computing & Infrastructure"
						},
						"value": "Cloud Computing & Infrastructure"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Consumer Technology"
						},
						"value": "Consumer Technology"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Cyber Security & Privacy"
						},
						"value": "Cyber Security & Privacy"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Data Science & AI"
						},
						"value": "Data Science & AI"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Decentralised Computing"
						},
						"value": "Decentralised Computing"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Digital Transformation"
						},
						"value": "Digital Transformation"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "IT & Network Infrastructure"
						},
						"value": "IT & Network Infrastructure"
					}
				],
				"action_id": "checkboxes-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Please select the news category you want to see."
			}
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Submit"
					},
					"value": "category_select",
					"action_id": "category_select"
				}
			]
		}
	]
