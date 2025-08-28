import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Typography, Alert, Spin } from 'antd';
import { 
  CarOutlined, 
  DatabaseOutlined, 
  ExperimentOutlined, 
  LineChartOutlined 
} from '@ant-design/icons';
import { vehicleAPI, batteryDataAPI, modelAPI } from '../services/api';
import BatteryHealthChart from '../components/BatteryHealthChart';

const { Title } = Typography;

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    vehicles: 0,
    totalData: 0,
    models: 0,
    predictions: 0
  });
  const [recentData, setRecentData] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Get vehicles
      const vehiclesResponse = await vehicleAPI.getVehicles();
      const vehicles = vehiclesResponse.data;
      
      // Get models for all vehicles
      const modelsResponse = await modelAPI.getModels();
      const models = modelsResponse.data;
      
      // Get recent battery data for the first vehicle (if any)
      let batteryData = [];
      let totalDataPoints = 0;
      
      if (vehicles.length > 0) {
        for (const vehicle of vehicles) {
          try {
            const dataResponse = await batteryDataAPI.getBatteryData(vehicle.id, { limit: 10 });
            batteryData = [...batteryData, ...dataResponse.data];
            
            // Get total count for this vehicle
            const allDataResponse = await batteryDataAPI.getBatteryData(vehicle.id, { limit: 1000 });
            totalDataPoints += allDataResponse.data.length;
          } catch (err) {
            console.error(`Error loading data for vehicle ${vehicle.id}:`, err);
          }
        }
      }
      
      setStats({
        vehicles: vehicles.length,
        totalData: totalDataPoints,
        models: models.length,
        predictions: models.filter(m => m.is_trained).length
      });
      
      // Sort by timestamp and take most recent
      setRecentData(
        batteryData
          .sort((a, b) => new Date(b.measurement_timestamp) - new Date(a.measurement_timestamp))
          .slice(0, 20)
      );
      
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <Title level={2}>Dashboard</Title>
      
      {error && (
        <Alert
          message={error}
          type="error"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Vehicles"
              value={stats.vehicles}
              prefix={<CarOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Data Points"
              value={stats.totalData}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="ML Models"
              value={stats.models}
              prefix={<ExperimentOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Trained Models"
              value={stats.predictions}
              prefix={<LineChartOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card title="Recent Battery Health Trends" className="dashboard-card">
            {recentData.length > 0 ? (
              <BatteryHealthChart data={recentData} height={300} />
            ) : (
              <div style={{ textAlign: 'center', padding: '50px' }}>
                <Typography.Text type="secondary">
                  No battery data available. Upload some data to see trends.
                </Typography.Text>
              </div>
            )}
          </Card>
        </Col>
        
        <Col xs={24} lg={8}>
          <Card title="Quick Stats" className="dashboard-card">
            <div style={{ textAlign: 'center' }}>
              {recentData.length > 0 ? (
                <>
                  <div className="stat-card">
                    <div className="stat-value" style={{ color: '#52c41a' }}>
                      {recentData[0]?.state_of_health?.toFixed(1) || 'N/A'}%
                    </div>
                    <div className="stat-label">Latest SOH</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value" style={{ color: '#1890ff' }}>
                      {recentData.filter(d => d.state_of_health > 80).length}
                    </div>
                    <div className="stat-label">Healthy Readings</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value" style={{ color: '#fa8c16' }}>
                      {recentData.filter(d => d.state_of_health <= 80).length}
                    </div>
                    <div className="stat-label">Warning Readings</div>
                  </div>
                </>
              ) : (
                <Typography.Text type="secondary">
                  No data available
                </Typography.Text>
              )}
            </div>
          </Card>
        </Col>
      </Row>

      {/* Model Performance Summary */}
      <Row gutter={[16, 16]}>
        <Col xs={24}>
          <Card title="Best Performing Models" className="dashboard-card">
            {stats.models > 0 ? (
              <div>
                <Typography.Text>
                  You have <strong>{stats.models}</strong> ML models, with <strong>{stats.predictions}</strong> trained models ready for predictions.
                </Typography.Text>
                <div style={{ marginTop: 16 }}>
                  <Typography.Text type="secondary">
                    Visit the Models page to view detailed performance metrics and create new models. 
                    Use the Predictions page to generate SOH forecasts and analyze threshold crossings.
                  </Typography.Text>
                </div>
              </div>
            ) : (
              <Alert
                message="No ML Models Created"
                description="Create your first ML model to start predicting battery health trends. Go to the Models page to get started."
                type="info"
                showIcon
              />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;