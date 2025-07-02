#!/usr/bin/env python3
"""
Sample MCP Server for Medical Appointment System
This server provides tools for managing medical appointments.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Sequence
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource, LoggingLevel
)
import mcp.types as types

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("medical-appointment-server")

# Sample data storage (in a real application, this would be a database)
DOCTORS = {
    "dr-smith-cardio": {
        "id": "dr-smith-cardio",
        "name": "Dr. John Smith",
        "specialization": "Cardiology",
        "available_slots": [
            "2025-06-04T14:00:00",
            "2025-06-04T15:00:00",
            "2025-06-05T10:00:00",
            "2025-06-05T11:00:00"
        ]
    },
    "dr-jones-derma": {
        "id": "dr-jones-derma",
        "name": "Dr. Sarah Jones",
        "specialization": "Dermatology",
        "available_slots": [
            "2025-06-04T09:00:00",
            "2025-06-04T13:00:00",
            "2025-06-05T14:00:00",
            "2025-06-05T16:00:00"
        ]
    }
}

APPOINTMENTS = {}
NEXT_APPOINTMENT_ID = 1

# Create a server instance
server = Server("medical-appointment-server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        Tool(
            name="search_available_doctors",
            description="Find available doctors by specialization and date",
            inputSchema={
                "type": "object",
                "properties": {
                    "specialization": {
                        "type": "string",
                        "description": "Medical specialization (e.g., cardiology, dermatology)"
                    },
                    "date": {
                        "type": "string",
                        "description": "Preferred date (YYYY-MM-DD format)"
                    }
                },
                "required": ["specialization"]
            },
        ),
        Tool(
            name="schedule_doctor_appointment",
            description="Schedule an appointment with a specific doctor",
            inputSchema={
                "type": "object",
                "properties": {
                    "doctor_id": {
                        "type": "string",
                        "description": "Doctor's unique identifier"
                    },
                    "patient_name": {
                        "type": "string",
                        "description": "Patient's full name"
                    },
                    "datetime": {
                        "type": "string",
                        "description": "Appointment datetime (ISO format)"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the appointment"
                    }
                },
                "required": ["doctor_id", "patient_name", "datetime"]
            },
        ),
        Tool(
            name="get_appointments",
            description="Get appointments for a patient or doctor",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_name": {
                        "type": "string",
                        "description": "Patient's name to search for"
                    },
                    "doctor_id": {
                        "type": "string",
                        "description": "Doctor's ID to search for"
                    },
                    "date_from": {
                        "type": "string",
                        "description": "Start date for search (YYYY-MM-DD)"
                    },
                    "date_to": {
                        "type": "string",
                        "description": "End date for search (YYYY-MM-DD)"
                    }
                }
            },
        ),
        Tool(
            name="cancel_appointment",
            description="Cancel an existing appointment",
            inputSchema={
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "string",
                        "description": "Unique appointment identifier"
                    }
                },
                "required": ["appointment_id"]
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    if arguments is None:
        arguments = {}

    if name == "search_available_doctors":
        specialization = arguments.get("specialization", "").lower()
        date = arguments.get("date")
        
        available_doctors = []
        for doctor_id, doctor in DOCTORS.items():
            if specialization in doctor["specialization"].lower():
                doctor_info = {
                    "id": doctor_id,
                    "name": doctor["name"],
                    "specialization": doctor["specialization"],
                    "available_slots": doctor["available_slots"]
                }
                if date:
                    # Filter slots by date
                    doctor_info["available_slots"] = [
                        slot for slot in doctor["available_slots"]
                        if slot.startswith(date)
                    ]
                available_doctors.append(doctor_info)
        
        result = {
            "doctors": available_doctors,
            "count": len(available_doctors)
        }
        
        return [
            types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )
        ]

    elif name == "schedule_doctor_appointment":
        global NEXT_APPOINTMENT_ID
        
        doctor_id = arguments.get("doctor_id")
        patient_name = arguments.get("patient_name")
        datetime_str = arguments.get("datetime")
        reason = arguments.get("reason", "General consultation")
        
        # Validate doctor exists
        if doctor_id not in DOCTORS:
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Doctor with ID {doctor_id} not found"})
                )
            ]
        
        # Check if the slot is available
        doctor = DOCTORS[doctor_id]
        if datetime_str not in doctor["available_slots"]:
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Time slot {datetime_str} is not available",
                        "available_slots": doctor["available_slots"]
                    })
                )
            ]
        
        # Create appointment
        appointment_id = str(NEXT_APPOINTMENT_ID)
        NEXT_APPOINTMENT_ID += 1
        
        appointment = {
            "id": appointment_id,
            "doctor_id": doctor_id,
            "doctor_name": doctor["name"],
            "patient_name": patient_name,
            "datetime": datetime_str,
            "reason": reason,
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }
        
        APPOINTMENTS[appointment_id] = appointment
        
        # Remove the slot from available slots
        DOCTORS[doctor_id]["available_slots"].remove(datetime_str)
        
        return [
            types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "appointment": appointment,
                    "message": f"Appointment scheduled successfully for {patient_name} with {doctor['name']} on {datetime_str}"
                }, indent=2)
            )
        ]

    elif name == "get_appointments":
        patient_name = arguments.get("patient_name")
        doctor_id = arguments.get("doctor_id")
        date_from = arguments.get("date_from")
        date_to = arguments.get("date_to")
        
        filtered_appointments = []
        
        for appointment in APPOINTMENTS.values():
            # Apply filters
            if patient_name and patient_name.lower() not in appointment["patient_name"].lower():
                continue
            if doctor_id and appointment["doctor_id"] != doctor_id:
                continue
            if date_from and appointment["datetime"] < date_from:
                continue
            if date_to and appointment["datetime"] > date_to:
                continue
            
            filtered_appointments.append(appointment)
        
        result = {
            "appointments": filtered_appointments,
            "count": len(filtered_appointments)
        }
        
        return [
            types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )
        ]

    elif name == "cancel_appointment":
        appointment_id = arguments.get("appointment_id")
        
        if appointment_id not in APPOINTMENTS:
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Appointment with ID {appointment_id} not found"})
                )
            ]
        
        appointment = APPOINTMENTS[appointment_id]
        
        # Add the slot back to available slots
        doctor_id = appointment["doctor_id"]
        if doctor_id in DOCTORS:
            DOCTORS[doctor_id]["available_slots"].append(appointment["datetime"])
            DOCTORS[doctor_id]["available_slots"].sort()
        
        # Mark as cancelled
        appointment["status"] = "cancelled"
        appointment["cancelled_at"] = datetime.now().isoformat()
        
        return [
            types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "message": f"Appointment {appointment_id} has been cancelled",
                    "appointment": appointment
                }, indent=2)
            )
        ]

    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="medical-appointment-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())