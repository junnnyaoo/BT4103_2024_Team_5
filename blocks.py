
#--------------------------------------------------------------------------------------------------------------------
#               Interactive message for category and schedule
#--------------------------------------------------------------------------------------------------------------------

news_sched_category_blocks = [
		{
			"type": "input",
			"block_id": "schedule_radiobuttons",
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
			"block_id": "category_checkboxes",
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
							"text": "AI"
						},
						"value": "AI"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Quantum Computing"
						},
						"value": "Quantum Computing"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Green Computing"
						},
						"value": "Green Computing"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Robotics"
						},
						"value": "Robotics"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Trust Technologies"
						},
						"value": "Trust Technologies"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Anti-disinformation technologies"
						},
						"value": "Anti-disinformation technologies"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Communications Technologies"
						},
						"value": "Communications Technologies"
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
			"block_id": "category_checkboxes",
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
							"text": "AI"
						},
						"value": "AI"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Quantum Computing"
						},
						"value": "Quantum Computing"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Green Computing"
						},
						"value": "Green Computing"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Robotics"
						},
						"value": "Robotics"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Trust Technologies"
						},
						"value": "Trust Technologies"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Anti-disinformation technologies"
						},
						"value": "Anti-disinformation technologies"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Communications Technologies"
						},
						"value": "Communications Technologies"
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
						"text": "Customize date period"
					},
					"value": "date_select",
					"action_id": "date_select"
				}
			]
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
#--------------------------------------------------------------------------------------------------------------------
#               Interactive message for date
#--------------------------------------------------------------------------------------------------------------------

news_date_block = 	[

	{
			"type": "rich_text",
			"elements": [
				{
					"type": "rich_text_section",
					"elements": [
						{
							"type": "text",
							"text": "Please customize the date range for the news you wish to view below.",
							"style": {
								"bold": True
							}
						}
					]
				}
			]
		},
		{
			"type": "input",
            "block_id" : "Start",
			"element": {
				"type": "datepicker",
				"initial_date": "2024-01-01",
				"placeholder": {
					"type": "plain_text",
					"text": "Select a date"
				},
				"action_id": "datepicker-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Start"
			}
		},
		{
			"type": "input",
            "block_id" : "End",
			"element": {
				"type": "datepicker",
				"initial_date": "2024-01-01",
				"placeholder": {
					"type": "plain_text",
					"text": "Select a date"
				},
				"action_id": "datepicker-action"
			},
			"label": {
				"type": "plain_text",
				"text": "End"
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
					"value": "date_selected",
					"action_id": "date_selected"
				}
			]
		}
	]