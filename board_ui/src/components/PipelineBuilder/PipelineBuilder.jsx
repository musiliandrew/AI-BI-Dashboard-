/**
 * Visual Drag-and-Drop Pipeline Builder
 * Mobile-first, intuitive interface for building data pipelines
 */
import React, { useState, useEffect, useCallback } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { TouchBackend } from 'react-dnd-touch-backend';
import { isMobile } from 'react-device-detect';
import { 
  Play, 
  Save, 
  Download, 
  Upload, 
  Settings, 
  Zap,
  Database,
  FileText,
  Globe,
  Filter,
  BarChart3,
  Brain,
  CheckCircle
} from 'lucide-react';

import NodePalette from './NodePalette';
import PipelineCanvas from './PipelineCanvas';
import NodeConfigPanel from './NodeConfigPanel';
import IndustryTemplateModal from './IndustryTemplateModal';
import IntelligencePanel from './IntelligencePanel';

const PipelineBuilder = () => {
  const [pipeline, setPipeline] = useState({
    id: null,
    name: 'New Pipeline',
    description: '',
    industry: 'retail',
    nodes: [],
    connections: [],
    canvas_config: {
      zoom: 1.0,
      pan_x: 0,
      pan_y: 0
    }
  });

  const [selectedNode, setSelectedNode] = useState(null);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [showIntelligence, setShowIntelligence] = useState(false);
  const [nodeTemplates, setNodeTemplates] = useState({});
  const [isExecuting, setIsExecuting] = useState(false);
  const [isMobileView, setIsMobileView] = useState(isMobile);

  // Responsive design detection
  useEffect(() => {
    const handleResize = () => {
      setIsMobileView(window.innerWidth < 768);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Load node templates on mount
  useEffect(() => {
    loadNodeTemplates();
  }, []);

  const loadNodeTemplates = async () => {
    try {
      const response = await fetch('/api/data-ingestion/visual-builder/?action=node_templates');
      const data = await response.json();
      setNodeTemplates(data.node_templates);
    } catch (error) {
      console.error('Failed to load node templates:', error);
    }
  };

  const createNewPipeline = async (name, description, industry) => {
    try {
      const response = await fetch('/api/data-ingestion/visual-builder/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, description, industry })
      });
      
      const data = await response.json();
      
      setPipeline(prev => ({
        ...prev,
        id: data.pipeline_id,
        name,
        description,
        industry
      }));
      
      return data.pipeline_id;
    } catch (error) {
      console.error('Failed to create pipeline:', error);
      throw error;
    }
  };

  const addNode = useCallback(async (nodeType, position) => {
    if (!pipeline.id) {
      // Create pipeline first if it doesn't exist
      await createNewPipeline(pipeline.name, pipeline.description, pipeline.industry);
    }

    try {
      const response = await fetch(`/api/data-ingestion/visual-builder/${pipeline.id}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'add_node',
          node_type: nodeType,
          position,
          config: {}
        })
      });

      const data = await response.json();
      
      // Add node to local state
      const template = nodeTemplates[Object.keys(nodeTemplates).find(cat => 
        nodeTemplates[cat].some(t => t.id === nodeType)
      )]?.find(t => t.id === nodeType);

      if (template) {
        const newNode = {
          id: data.node_id,
          type: template.type,
          name: template.name,
          description: template.description,
          icon: template.icon,
          config: {},
          position,
          inputs: [],
          outputs: [],
          status: 'configured'
        };

        setPipeline(prev => ({
          ...prev,
          nodes: [...prev.nodes, newNode]
        }));
      }
    } catch (error) {
      console.error('Failed to add node:', error);
    }
  }, [pipeline.id, pipeline.name, pipeline.description, pipeline.industry, nodeTemplates]);

  const connectNodes = useCallback(async (sourceNodeId, targetNodeId) => {
    if (!pipeline.id) return;

    try {
      const response = await fetch(`/api/data-ingestion/visual-builder/${pipeline.id}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'connect_nodes',
          source_node_id: sourceNodeId,
          target_node_id: targetNodeId
        })
      });

      const data = await response.json();
      
      // Add connection to local state
      const newConnection = {
        id: data.connection_id,
        source_node_id: sourceNodeId,
        target_node_id: targetNodeId,
        source_port: 'output',
        target_port: 'input'
      };

      setPipeline(prev => ({
        ...prev,
        connections: [...prev.connections, newConnection],
        nodes: prev.nodes.map(node => {
          if (node.id === sourceNodeId) {
            return { ...node, outputs: [...node.outputs, targetNodeId] };
          }
          if (node.id === targetNodeId) {
            return { ...node, inputs: [...node.inputs, sourceNodeId] };
          }
          return node;
        })
      }));
    } catch (error) {
      console.error('Failed to connect nodes:', error);
    }
  }, [pipeline.id]);

  const executePipeline = async () => {
    if (!pipeline.id || pipeline.nodes.length === 0) return;

    setIsExecuting(true);
    try {
      const response = await fetch(`/api/data-ingestion/visual-builder/${pipeline.id}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'execute'
        })
      });

      const data = await response.json();
      console.log('Pipeline execution started:', data);
      
      // You could add real-time status updates here via WebSocket
    } catch (error) {
      console.error('Failed to execute pipeline:', error);
    } finally {
      setIsExecuting(false);
    }
  };

  const updateNodeConfig = (nodeId, config) => {
    setPipeline(prev => ({
      ...prev,
      nodes: prev.nodes.map(node => 
        node.id === nodeId ? { ...node, config } : node
      )
    }));
  };

  const deleteNode = (nodeId) => {
    setPipeline(prev => ({
      ...prev,
      nodes: prev.nodes.filter(node => node.id !== nodeId),
      connections: prev.connections.filter(conn => 
        conn.source_node_id !== nodeId && conn.target_node_id !== nodeId
      )
    }));
  };

  const getNodeIcon = (nodeType) => {
    const iconMap = {
      'source': <Database className="w-4 h-4" />,
      'transform': <Filter className="w-4 h-4" />,
      'validate': <CheckCircle className="w-4 h-4" />,
      'ai': <Brain className="w-4 h-4" />,
      'output': <BarChart3 className="w-4 h-4" />
    };
    return iconMap[nodeType] || <FileText className="w-4 h-4" />;
  };

  return (
    <DndProvider backend={isMobileView ? TouchBackend : HTML5Backend}>
      <div className="h-screen flex flex-col bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-semibold text-gray-900">
                {pipeline.name}
              </h1>
              <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                {pipeline.industry}
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              {!isMobileView && (
                <>
                  <button
                    onClick={() => setShowIntelligence(true)}
                    className="p-2 text-gray-600 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                    title="AI Intelligence"
                  >
                    <Zap className="w-5 h-5" />
                  </button>
                  
                  <button
                    onClick={() => setShowTemplateModal(true)}
                    className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Templates"
                  >
                    <Upload className="w-5 h-5" />
                  </button>
                </>
              )}
              
              <button
                onClick={executePipeline}
                disabled={isExecuting || pipeline.nodes.length === 0}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Play className="w-4 h-4" />
                <span className="hidden sm:inline">
                  {isExecuting ? 'Running...' : 'Execute'}
                </span>
              </button>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Node Palette - Collapsible on mobile */}
          {(!isMobileView || !selectedNode) && (
            <div className={`${isMobileView ? 'w-full' : 'w-80'} bg-white border-r border-gray-200 flex flex-col`}>
              <NodePalette
                nodeTemplates={nodeTemplates}
                onAddNode={addNode}
                isMobile={isMobileView}
              />
            </div>
          )}

          {/* Canvas */}
          {(!isMobileView || !selectedNode) && (
            <div className="flex-1 relative">
              <PipelineCanvas
                pipeline={pipeline}
                onNodeSelect={setSelectedNode}
                onNodeConnect={connectNodes}
                onNodeDelete={deleteNode}
                getNodeIcon={getNodeIcon}
                isMobile={isMobileView}
              />
            </div>
          )}

          {/* Configuration Panel */}
          {selectedNode && (
            <div className={`${isMobileView ? 'w-full' : 'w-96'} bg-white border-l border-gray-200`}>
              <NodeConfigPanel
                node={selectedNode}
                onConfigChange={(config) => updateNodeConfig(selectedNode.id, config)}
                onClose={() => setSelectedNode(null)}
                isMobile={isMobileView}
              />
            </div>
          )}
        </div>

        {/* Mobile Bottom Navigation */}
        {isMobileView && (
          <div className="bg-white border-t border-gray-200 px-4 py-2">
            <div className="flex justify-around">
              <button
                onClick={() => setShowTemplateModal(true)}
                className="flex flex-col items-center p-2 text-gray-600"
              >
                <Upload className="w-5 h-5" />
                <span className="text-xs mt-1">Templates</span>
              </button>
              
              <button
                onClick={() => setShowIntelligence(true)}
                className="flex flex-col items-center p-2 text-gray-600"
              >
                <Zap className="w-5 h-5" />
                <span className="text-xs mt-1">AI Help</span>
              </button>
              
              <button
                onClick={executePipeline}
                disabled={isExecuting || pipeline.nodes.length === 0}
                className="flex flex-col items-center p-2 text-green-600"
              >
                <Play className="w-5 h-5" />
                <span className="text-xs mt-1">Run</span>
              </button>
            </div>
          </div>
        )}

        {/* Modals */}
        {showTemplateModal && (
          <IndustryTemplateModal
            industry={pipeline.industry}
            onClose={() => setShowTemplateModal(false)}
            onSelectTemplate={(template) => {
              // Load template into pipeline
              console.log('Loading template:', template);
              setShowTemplateModal(false);
            }}
          />
        )}

        {showIntelligence && (
          <IntelligencePanel
            onClose={() => setShowIntelligence(false)}
            onRecommendation={(recommendation) => {
              // Apply AI recommendation
              console.log('Applying recommendation:', recommendation);
            }}
          />
        )}
      </div>
    </DndProvider>
  );
};

export default PipelineBuilder;
