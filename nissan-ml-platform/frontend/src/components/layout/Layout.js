// frontend/src/components/layout/Layout.js
import React, { useState } from 'react';
import { useNavigate, Link as RouterLink, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Menu,
  MenuItem,
  Container,
  Hidden,
  CssBaseline,
  Tooltip,
  Avatar,
  ListItemButton
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Storage,
  BarChart,
  ExitToApp,
  Person,
  Settings,
  CloudUpload,
  Psychology,
  ChevronLeft,
} from '@mui/icons-material';
import nissan_logo from '../../assets/nissan-logo.png';

// Ancho del drawer
const drawerWidth = 240;

const Layout = ({ children }) => {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  
  // Manejar apertura/cierre del drawer
  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };
  
  // Manejar apertura del menú de usuario
  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  // Manejar cierre del menú de usuario
  const handleMenuClose = () => {
    setAnchorEl(null);
  };
  
  // Manejar logout
  const handleLogout = () => {
    handleMenuClose();
    logout();
    navigate('/login');
  };
  
  // Elementos del menú lateral
  const menuItems = [
    { text: 'Dashboard', icon: <Dashboard />, path: '/dashboard' },
    { text: 'Mis Archivos', icon: <Storage />, path: '/files' },
    { text: 'Subir Archivo', icon: <CloudUpload />, path: '/upload' },
    { text: 'Modelos ML', icon: <Psychology />, path: '/models' },
    { text: 'Análisis', icon: <BarChart />, path: '/analysis' }
  ];
  
  // Determinar si una ruta está activa
  const isActive = (path) => {
    return location.pathname === path;
  };
  
  // Contenido del drawer
  const drawer = (
    <Box>
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center',
        justifyContent: 'space-between',
        p: 2 
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <img src={nissan_logo} alt="Nissan Logo" style={{ height: 40 }} />
          <Typography variant="h6" sx={{ ml: 1, fontWeight: 'bold' }}>
            ML Platform
          </Typography>
        </Box>
        <Hidden smUp>
          <IconButton onClick={handleDrawerToggle}>
            <ChevronLeft />
          </IconButton>
        </Hidden>
      </Box>
      
      <Divider />
      
      <List>
        {menuItems.map((item) => (
          <ListItem 
            key={item.text} 
            disablePadding
            component={RouterLink}
            to={item.path}
            sx={{ color: 'inherit', textDecoration: 'none' }}
          >
            <ListItemButton
              selected={isActive(item.path)}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: 'primary.main',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  },
                }
              }}
            >
              <ListItemIcon sx={{ 
                color: isActive(item.path) ? 'white' : 'inherit' 
              }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      
      <Divider sx={{ mt: 2 }} />
      
      <Box sx={{ p: 2 }}>
        <Typography variant="caption" color="textSecondary">
          Nissan ML Platform v1.0.0
        </Typography>
      </Box>
    </Box>
  );
  
  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      
      {/* AppBar */}
      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          boxShadow: 1,
          backgroundColor: 'white',
          color: 'text.primary'
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Hidden smDown>
            <img src={nissan_logo} alt="Nissan Logo" style={{ height: 30, marginRight: 16 }} />
            <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
              Nissan ML Platform
            </Typography>
          </Hidden>
          
          <Hidden smUp>
            <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
              Nissan ML
            </Typography>
          </Hidden>
          
          {currentUser ? (
            <>
              <Tooltip title="Opciones de usuario">
                <IconButton
                  onClick={handleMenuOpen}
                  size="small"
                  sx={{ ml: 2 }}
                >
                  <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                    {currentUser.username?.charAt(0).toUpperCase() || 'U'}
                  </Avatar>
                </IconButton>
              </Tooltip>
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
              >
                <MenuItem disabled>
                  <Typography variant="body2">
                    {currentUser.full_name || currentUser.username}
                  </Typography>
                </MenuItem>
                <Divider />
                <MenuItem onClick={handleMenuClose} component={RouterLink} to="/profile">
                  <ListItemIcon>
                    <Person fontSize="small" />
                  </ListItemIcon>
                  <ListItemText>Perfil</ListItemText>
                </MenuItem>
                <MenuItem onClick={handleMenuClose} component={RouterLink} to="/settings">
                  <ListItemIcon>
                    <Settings fontSize="small" />
                  </ListItemIcon>
                  <ListItemText>Ajustes</ListItemText>
                </MenuItem>
                <Divider />
                <MenuItem onClick={handleLogout}>
                  <ListItemIcon>
                    <ExitToApp fontSize="small" />
                  </ListItemIcon>
                  <ListItemText>Cerrar sesión</ListItemText>
                </MenuItem>
              </Menu>
            </>
          ) : (
            <Button color="primary" variant="contained" component={RouterLink} to="/login">
              Iniciar Sesión
            </Button>
          )}
        </Toolbar>
      </AppBar>
      
      {/* Drawer */}
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        {/* Drawer móvil */}
        <Drawer
          variant="temporary"
          open={drawerOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Mejor rendimiento en móviles
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        
        {/* Drawer permanente (escritorio) */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box' },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      
      {/* Contenido principal */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: '64px', // Altura del AppBar
          backgroundColor: '#f5f5f5',
          minHeight: 'calc(100vh - 64px)'
        }}
      >
        <Container maxWidth="xl">
          {children}
        </Container>
      </Box>
    </Box>
  );
};

export default Layout;