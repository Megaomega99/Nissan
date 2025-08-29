import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Layout as AntLayout,
  Menu,
  Avatar,
  Dropdown,
  Typography,
  Space,
} from 'antd';
import {
  DashboardOutlined,
  CarOutlined,
  UploadOutlined,
  ExperimentOutlined,
  LineChartOutlined,
  UserOutlined,
  LogoutOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';

const { Header, Sider, Content } = AntLayout;
const { Title } = Typography;

const Layout = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/vehicles',
      icon: <CarOutlined />,
      label: 'Vehicles',
    },
    {
      key: '/data-upload',
      icon: <UploadOutlined />,
      label: 'Data Upload',
    },
    {
      key: '/models',
      icon: <ExperimentOutlined />,
      label: 'ML Models',
    },
    {
      key: '/predictions',
      icon: <LineChartOutlined />,
      label: 'Predictions',
    },
  ];

  const userMenuItems = [
    {
      key: 'profile',
      label: 'Profile',
      icon: <UserOutlined />,
    },
    {
      key: 'settings',
      label: 'Settings',
      icon: <SettingOutlined />,
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      label: 'Logout',
      icon: <LogoutOutlined />,
      onClick: logout,
    },
  ];

  const onMenuClick = ({ key }) => {
    navigate(key);
  };

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        theme="dark"
        style={{
          position: 'fixed',
          height: '100vh',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div style={{ 
          height: 64, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          borderBottom: '1px solid #303030'
        }}>
          <Title 
            level={4} 
            style={{ 
              color: 'white', 
              margin: 0,
              fontSize: collapsed ? '16px' : '18px'
            }}
          >
            {collapsed ? 'EV' : 'EV Predictor'}
          </Title>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={onMenuClick}
          style={{ marginTop: 8 }}
        />
      </Sider>
      
      <AntLayout style={{ marginLeft: collapsed ? 80 : 200 }}>
        <Header 
          style={{ 
            position: 'fixed',
            top: 0,
            right: 0,
            width: `calc(100% - ${collapsed ? 80 : 200}px)`,
            background: 'white',
            padding: '0 24px',
            display: 'flex',
            justifyContent: 'flex-end',
            alignItems: 'center',
            borderBottom: '1px solid #f0f0f0',
            zIndex: 1000,
          }}
        >
          <Dropdown
            menu={{
              items: userMenuItems,
            }}
            trigger={['click']}
          >
            <Space style={{ cursor: 'pointer' }}>
              <Avatar icon={<UserOutlined />} />
              <span>{user?.first_name || user?.username || 'User'}</span>
            </Space>
          </Dropdown>
        </Header>
        
        <Content 
          style={{ 
            margin: '88px 24px 24px',
            padding: 24,
            background: 'white',
            borderRadius: 8,
          }}
        >
          {children}
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;