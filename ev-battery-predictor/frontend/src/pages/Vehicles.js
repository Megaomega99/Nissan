import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Card,
  Button,
  Table,
  Modal,
  Form,
  Input,
  InputNumber,
  Space,
  Popconfirm,
  message,
  Tag,
  Row,
  Col,
  Alert
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  CarOutlined
} from '@ant-design/icons';
import { vehicleAPI } from '../services/api';
import { handleApiError } from '../utils/errorHandling';

const { Title } = Typography;

const Vehicles = () => {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState(null);
  const [form] = Form.useForm();
  const navigate = useNavigate();

  const loadVehicles = async () => {
    try {
      setLoading(true);
      const response = await vehicleAPI.getVehicles();
      setVehicles(response.data);
    } catch (error) {
      const errorMsg = handleApiError(error, 'Failed to load vehicles');
      message.error(errorMsg.error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVehicles();
  }, []);

  const handleCreateEdit = async (values) => {
    try {
      if (editingVehicle) {
        await vehicleAPI.updateVehicle(editingVehicle.id, values);
        message.success('Vehicle updated successfully');
      } else {
        await vehicleAPI.createVehicle(values);
        message.success('Vehicle created successfully');
      }
      
      setModalVisible(false);
      setEditingVehicle(null);
      form.resetFields();
      loadVehicles();
    } catch (error) {
      const errorMsg = handleApiError(error, 'Failed to save vehicle');
      message.error(errorMsg.error);
    }
  };

  const handleDelete = async (id) => {
    try {
      await vehicleAPI.deleteVehicle(id);
      message.success('Vehicle deleted successfully');
      loadVehicles();
    } catch (error) {
      const errorMsg = handleApiError(error, 'Failed to delete vehicle');
      message.error(errorMsg.error);
    }
  };

  const handleEdit = (vehicle) => {
    setEditingVehicle(vehicle);
    form.setFieldsValue(vehicle);
    setModalVisible(true);
  };

  const handleView = (vehicle) => {
    navigate(`/vehicles/${vehicle.id}`);
  };

  const openCreateModal = () => {
    setEditingVehicle(null);
    form.resetFields();
    setModalVisible(true);
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space>
          <CarOutlined style={{ color: '#1890ff' }} />
          <strong>{text}</strong>
        </Space>
      ),
    },
    {
      title: 'Make & Model',
      key: 'makeModel',
      render: (_, record) => (
        <span>
          {record.make && record.model ? `${record.make} ${record.model}` : 'Not specified'}
        </span>
      ),
    },
    {
      title: 'Year',
      dataIndex: 'year',
      key: 'year',
      render: (year) => year || 'Not specified',
    },
    {
      title: 'Battery',
      key: 'battery',
      render: (_, record) => (
        <div>
          {record.battery_capacity && (
            <Tag color="blue">{record.battery_capacity} kWh</Tag>
          )}
          {record.battery_type && (
            <Tag color="green">{record.battery_type}</Tag>
          )}
        </div>
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
            size="small"
          >
            View
          </Button>
          <Button
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            size="small"
          >
            Edit
          </Button>
          <Popconfirm
            title="Delete Vehicle"
            description="Are you sure you want to delete this vehicle? This will also delete all associated battery data and models."
            onConfirm={() => handleDelete(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Button
              danger
              icon={<DeleteOutlined />}
              size="small"
            >
              Delete
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Title level={2}>Vehicles</Title>
        </Col>
        <Col>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={openCreateModal}
            size="large"
          >
            Add Vehicle
          </Button>
        </Col>
      </Row>

      {vehicles.length === 0 && !loading && (
        <Alert
          message="No vehicles found"
          description="Get started by adding your first electric vehicle to monitor its battery health."
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      <Card>
        <Table
          columns={columns}
          dataSource={vehicles}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `Total ${total} vehicles`,
          }}
        />
      </Card>

      <Modal
        title={editingVehicle ? 'Edit Vehicle' : 'Add New Vehicle'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setEditingVehicle(null);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateEdit}
          initialValues={{
            battery_type: 'Lithium Ion'
          }}
        >
          <Form.Item
            name="name"
            label="Vehicle Name"
            rules={[
              { required: true, message: 'Please enter vehicle name' },
              { min: 2, message: 'Name must be at least 2 characters' },
            ]}
          >
            <Input placeholder="e.g., My Tesla Model 3" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="make"
                label="Make"
              >
                <Input placeholder="e.g., Tesla" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="model"
                label="Model"
              >
                <Input placeholder="e.g., Model 3" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="year"
                label="Year"
              >
                <InputNumber
                  min={1990}
                  max={new Date().getFullYear() + 1}
                  placeholder="2023"
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="battery_capacity"
                label="Battery Capacity (kWh)"
              >
                <InputNumber
                  min={1}
                  max={1000}
                  step={0.1}
                  placeholder="75.0"
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="battery_type"
            label="Battery Type"
          >
            <Input placeholder="e.g., Lithium Ion" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setModalVisible(false)}>
                Cancel
              </Button>
              <Button type="primary" htmlType="submit">
                {editingVehicle ? 'Update' : 'Create'} Vehicle
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Vehicles;