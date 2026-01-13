# Viviz Bulk Sender - User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Managing Contacts](#managing-contacts)
4. [Creating Campaigns](#creating-campaigns)
5. [Chat Inbox](#chat-inbox)
6. [Analytics & Reports](#analytics--reports)
7. [Settings](#settings)
8. [Billing & Subscription](#billing--subscription)

---

## Getting Started

### Account Setup

1. **Sign Up**
   - Visit the registration page
   - Enter your email, name, and password
   - Verify your email address

2. **Organization Setup**
   - Create your organization name
   - Set your timezone and language preferences

3. **Connect WhatsApp**
   - Navigate to Settings > WhatsApp Connection
   - Enter your Green API credentials
   - Scan the QR code to connect your WhatsApp account

---

## Dashboard Overview

The dashboard provides a quick overview of your messaging activity:

- **Total Messages**: Cumulative messages sent
- **Today's Messages**: Messages sent today
- **Total Contacts**: Number of contacts in your CRM
- **Active Campaigns**: Currently running campaigns

### Quick Actions

- **Create Campaign**: Start a new bulk messaging campaign
- **Add Contacts**: Import or add new contacts
- **Open Chats**: View and manage conversations

---

## Managing Contacts

### Adding Contacts

**Manual Entry**
1. Go to Contacts page
2. Click "Add Contact"
3. Enter phone number, name, email, and tags
4. Save the contact

**Bulk Import**
1. Go to Contacts page
2. Click "Import"
3. Upload a CSV or Excel file
4. Map the columns to contact fields
5. Confirm the import

### Contact Fields

| Field | Description |
|-------|-------------|
| Phone | WhatsApp phone number (with country code) |
| Name | Contact's display name |
| Email | Email address |
| Company | Company name |
| Tags | Custom tags for segmentation |

### Using Tags

Tags help you organize and segment contacts:

1. Create tags in Settings > Tags
2. Assign tags to contacts
3. Filter campaigns by tag

Example: Tag contacts as "VIP", "Newsletter", "New Customer"

---

## Creating Campaigns

### Campaign Types

1. **Broadcast**: Send to all contacts or filtered segments
2. **Scheduled**: Schedule for future delivery
3. **Recurring**: Repeat on daily/weekly/monthly basis

### Campaign Steps

1. **Create Campaign**
   - Name your campaign
   - Add description (optional)

2. **Write Message**
   - Enter your message content
   - Use variables for personalization:
     - `{name}` - Contact's name
     - `{company}` - Company name
     - `{email}` - Email address

3. **Add Media** (Optional)
   - Upload images, videos, documents
   - Add captions

4. **Select Recipients**
   - All contacts
   - By tag
   - By custom filter

5. **Set Schedule**
   - Send immediately
   - Schedule for specific date/time
   - Set recurring schedule

6. **Review & Launch**
   - Preview message
   - Check recipient count
   - Launch or schedule

### Message Personalization

```
Hello {name}!

Thank you for being a {membership_type} member at {company}.

Best regards,
The Team
```

---

## Chat Inbox

### Features

- **Real-time messaging**: Receive and reply to messages
- **Multi-conversation**: Manage multiple chats
- **Assign agents**: Assign chats to team members
- **Auto-reply**: Set up automatic responses

### Auto-Reply Rules

1. Go to Settings > Auto-Reply
2. Create a new rule
3. Set trigger (keyword, exact match, or always)
4. Configure response message
5. Set priority

### Chat Actions

- **Archive**: Hide chat from active list
- **Block**: Block the contact
- **Assign**: Assign to team member
- **Add Note**: Add internal notes

---

## Analytics & Reports

### Available Reports

1. **Message Statistics**
   - Sent, delivered, read counts
   - Delivery rate
   - Read rate

2. **Campaign Performance**
   - Progress tracking
   - Engagement metrics
   - Comparison across campaigns

3. **Contact Engagement**
   - Most active contacts
   - Response rates
   - Conversation history

### Exporting Reports

1. Go to Analytics page
2. Select date range
3. Choose export format (CSV, PDF)
4. Download report

---

## Settings

### Organization Settings

- **Profile**: Update organization name, logo
- **Contact Info**: Email, phone, address
- **Branding**: Custom colors and logo

### WhatsApp Connection

- **Green API Credentials**: ID, Token, Instance ID
- **Connection Status**: Check if connected
- **QR Code**: For re-connecting

### Notification Preferences

- **Email Notifications**: Campaign updates, alerts
- **Browser Notifications**: New messages

### Team Management

- **Invite Members**: Send invitations
- **Manage Roles**: Admin, Manager, Agent, Viewer
- **Remove Members**: Revoke access

---

## Billing & Subscription

### Subscription Plans

| Plan | Messages | Contacts | Features |
|------|----------|----------|----------|
| Free | 100/mo | 50 | Basic |
| Basic | 5,000/mo | 1,000 | Email support |
| Pro | 25,000/mo | 10,000 | Priority support |
| Enterprise | Unlimited | Unlimited | Custom features |

### Managing Subscription

1. Go to Settings > Subscription
2. View current plan
3. Upgrade or downgrade
4. Update payment method

### Billing History

- View past invoices
- Download receipts
- Update billing information

---

## Troubleshooting

### Common Issues

**WhatsApp Not Connecting**
- Verify Green API credentials
- Check QR code scanning
- Ensure WhatsApp is installed

**Messages Not Sending**
- Check rate limits
- Verify contact numbers
- Check Green API balance

**Contacts Not Importing**
- Check file format
- Verify phone number format
- Check for duplicate entries

### Getting Support

- Email: support@vivizbulksender.com
- Documentation: [docs.vivizbulksender.com]
- Help Center: [help.vivizbulksender.com]

---

## Best Practices

### Message Best Practices

1. **Personalize Messages**
   - Use contact names
   - Segment your audience

2. **Timing**
   - Send during business hours
   - Consider time zones

3. **Content**
   - Keep messages concise
   - Include clear call-to-action

4. **Compliance**
   - Get consent before messaging
   - Include unsubscribe option

### Contact Management

1. **Regular Cleanup**
   - Remove invalid numbers
   - Update outdated information

2. **Segmentation**
   - Use tags effectively
   - Create targeted campaigns

---

## Security & Privacy

### Data Protection

- All data encrypted in transit
- Regular backups
- No data sharing with third parties

### Privacy Settings

- Control data retention
- Export your data
- Request data deletion

---

## API Documentation

For developers, API documentation is available at:

- Swagger UI: `/api/schema/`
- ReDoc: `/api/docs/`

### Authentication

All API requests require JWT authentication:

```
Authorization: Bearer <your_access_token>
```

### Rate Limits

| Plan | Requests/Hour |
|------|---------------|
| Free | 100 |
| Basic | 500 |
| Pro | 1,000 |
| Enterprise | Custom |

---

*Last updated: January 2025*
