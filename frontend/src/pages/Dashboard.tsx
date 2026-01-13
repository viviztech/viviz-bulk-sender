import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { MessageSquare, Users, Send, TrendingUp } from 'lucide-react';

export default function Dashboard() {
  const { data: analytics } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => axios.get('/api/analytics/overview/').then(res => res.data),
  });

  const stats = analytics?.data || {
    messages: { total: 0, today: 0 },
    contacts: { total: 0, blocked: 0 },
    campaigns: { total: 0, active: 0 },
  };

  const statCards = [
    { label: 'Total Messages', value: stats.messages.total, icon: MessageSquare, color: 'text-green-600' },
    { label: 'Today\'s Messages', value: stats.messages.today, icon: TrendingUp, color: 'text-blue-600' },
    { label: 'Total Contacts', value: stats.contacts.total, icon: Users, color: 'text-purple-600' },
    { label: 'Active Campaigns', value: stats.campaigns.active, icon: Send, color: 'text-orange-600' },
  ];

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="text-gray-600">Welcome to Viviz Bulk Sender</p>
      </div>

      <div className="stats-grid">
        {statCards.map((stat, index) => (
          <div key={index} className="stat-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="stat-label">{stat.label}</p>
                <p className="stat-value">{stat.value}</p>
              </div>
              <stat.icon className={`w-10 h-10 ${stat.color}`} />
            </div>
          </div>
        ))}
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        <div className="flex gap-4">
          <a href="/campaigns" className="btn btn-primary">Create Campaign</a>
          <a href="/contacts" className="btn btn-secondary">Add Contacts</a>
          <a href="/chats" className="btn btn-secondary">Open Chats</a>
        </div>
      </div>
    </div>
  );
}
