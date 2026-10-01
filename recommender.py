def generate_recommendation(planner_type, data):

    # -------------------------
    # HOME INTERIOR PLANNER
    # -------------------------
    if planner_type == "home":

        budget = data.get("budget", "")
        rooms = data.get("rooms", "")
        quantities = data.get("quantities", "")

        return {
            "title": "Home Interior Recommendations",

            "budget": budget,

            "details": {
                "rooms": rooms,
                "quantities": quantities
            },

            "suggestions": [
                {
                    "item": "LED Lights",
                    "reason": "Energy efficient and budget friendly"
                },
                {
                    "item": "Ceiling Fan",
                    "reason": "Useful for living room and bedrooms"
                },
                {
                    "item": "Study Table",
                    "reason": "Suitable for a compact home workspace"
                },
                {
                    "item": "Storage Cabinet",
                    "reason": "Helps organize household items"
                }
            ]
        }

    # -------------------------
    # PARTY PLANNER
    # -------------------------
    elif planner_type == "party":

        budget = data.get("budget", "")
        guests = data.get("guests", "")
        event_type = data.get("event_type", "")
        venue = data.get("venue", "")

        return {
            "title": "Party Planning Recommendations",

            "budget": budget,

            "details": {
                "guests": guests,
                "event_type": event_type,
                "venue": venue
            },

            "budget_allocation": [
                {
                    "category": "Catering",
                    "percentage": "50%"
                },
                {
                    "category": "Decoration",
                    "percentage": "20%"
                },
                {
                    "category": "Entertainment",
                    "percentage": "20%"
                },
                {
                    "category": "Other Expenses",
                    "percentage": "10%"
                }
            ],

            "suggestions": [
                {
                    "item": "Catering",
                    "reason": "Plan food according to guest count"
                },
                {
                    "item": "Decoration",
                    "reason": "Choose decoration according to event type"
                },
                {
                    "item": "Music / Entertainment",
                    "reason": "Suitable for social events"
                }
            ]
        }

    # -------------------------
    # JEWELRY PLANNER
    # -------------------------
    elif planner_type == "jewelry":

        budget = data.get("budget", "")
        occasion = data.get("occasion", "")
        style = data.get("style", "")

        return {
            "title": "Jewelry Recommendations",

            "budget": budget,

            "details": {
                "occasion": occasion,
                "style": style
            },

            "suggestions": [
                {
                    "item": "Necklace",
                    "reason": "Suitable for traditional and special occasions"
                },
                {
                    "item": "Earrings",
                    "reason": "Easy to match with different outfits"
                },
                {
                    "item": "Bangles",
                    "reason": "Suitable for traditional styling"
                },
                {
                    "item": "Ring",
                    "reason": "Simple accessory for everyday or special use"
                }
            ]
        }

    # -------------------------
    # INVALID PLANNER
    # -------------------------
    else:

        return {
            "title": "Unknown Planner",

            "suggestions": [
                {
                    "item": "Please select Home, Party or Jewelry",
                    "reason": "Planner type was not recognized"
                }
            ]
        }