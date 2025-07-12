/**
 * Pipeline Canvas - Interactive canvas for building data pipelines
 */
import React, { useState, useRef, useCallback } from 'react';
import { useDrop } from 'react-dnd';
import { 
  Trash2, 
  Settings, 
  Play,
  AlertCircle,
  CheckCircle,
  Clock,
  Zap
} from 'lucide-react';

const PipelineNode = ({ 
  node, 
  onSelect, 
  onDelete, 
  onConnect, 
  getNodeIcon, 
  isSelected,
  isMobile 
}) => {
  const [isConnecting, setIsConnecting] = useState(false);
  const nodeRef = useRef(null);

  const getStatusColor = (status) => {
    const colorMap = {
      'configured': 'border-gray-300 bg-white',
      'running': 'border-blue-500 bg-blue-50',
      'completed': 'border-green-500 bg-green-50',
      'error': 'border-red-500 bg-red-50'
    };
    return colorMap[status] || 'border-gray-300 bg-white';
  };

  const getStatusIcon = (status) => {
    const iconMap = {
      'configured': <Settings className="w-3 h-3 text-gray-400" />,
      'running': <Clock className="w-3 h-3 text-blue-500" />,
      'completed': <CheckCircle className="w-3 h-3 text-green-500" />,
      'error': <AlertCircle className="w-3 h-3 text-red-500" />
    };
    return iconMap[status] || <Settings className="w-3 h-3 text-gray-400" />;
  };

  const handleNodeClick = () => {
    if (isConnecting) {
      // Handle connection logic
      setIsConnecting(false);
    } else {
      onSelect(node);
    }
  };

  const handleConnectionStart = (e) => {
    e.stopPropagation();
    setIsConnecting(true);
  };

  return (
    <div
      ref={nodeRef}
      className={`
        absolute cursor-pointer transition-all duration-200 select-none
        ${isSelected ? 'z-20' : 'z-10'}
      `}
      style={{
        left: node.position.x,
        top: node.position.y,
        transform: isSelected ? 'scale(1.05)' : 'scale(1)'
      }}
      onClick={handleNodeClick}
    >
      {/* Node Body */}
      <div className={`
        relative p-4 rounded-lg border-2 shadow-lg min-w-[200px] max-w-[250px]
        ${getStatusColor(node.status)}
        ${isSelected ? 'ring-2 ring-blue-500 ring-opacity-50' : ''}
        ${isConnecting ? 'ring-2 ring-purple-500 ring-opacity-50' : ''}
        hover:shadow-xl transition-shadow
      `}>
        {/* Header */}
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center space-x-2 flex-1">
            <div className="flex-shrink-0">
              {node.icon ? (
                <span className="text-lg">{node.icon}</span>
              ) : (
                getNodeIcon(node.type)
              )}
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-medium text-gray-900 truncate">
                {node.name}
              </h3>
            </div>
          </div>
          
          <div className="flex items-center space-x-1 ml-2">
            {getStatusIcon(node.status)}
            {!isMobile && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(node.id);
                }}
                className="p-1 text-gray-400 hover:text-red-500 transition-colors"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            )}
          </div>
        </div>

        {/* Description */}
        <p className="text-xs text-gray-600 mb-3 line-clamp-2">
          {node.description}
        </p>

        {/* Connection Points */}
        <div className="flex justify-between items-center">
          {/* Input Port */}
          {node.inputs.length > 0 || ['transform', 'validate', 'ai', 'output'].includes(node.type) ? (
            <div className="w-3 h-3 bg-blue-500 rounded-full border-2 border-white shadow-sm -ml-6 relative z-10" />
          ) : (
            <div className="w-3" />
          )}

          {/* Configuration Indicator */}
          <div className="flex items-center space-x-1">
            {Object.keys(node.config).length > 0 && (
              <div className="w-2 h-2 bg-green-500 rounded-full" title="Configured" />
            )}
          </div>

          {/* Output Port */}
          {node.outputs.length > 0 || ['source', 'transform', 'validate', 'ai'].includes(node.type) ? (
            <button
              onClick={handleConnectionStart}
              className="w-3 h-3 bg-green-500 rounded-full border-2 border-white shadow-sm -mr-6 relative z-10 hover:scale-125 transition-transform"
              title="Connect to next node"
            />
          ) : (
            <div className="w-3" />
          )}
        </div>

        {/* Mobile Actions */}
        {isMobile && isSelected && (
          <div className="mt-3 pt-3 border-t border-gray-200 flex justify-between">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(node.id);
              }}
              className="flex items-center space-x-1 px-2 py-1 text-xs text-red-600 hover:bg-red-50 rounded"
            >
              <Trash2 className="w-3 h-3" />
              <span>Delete</span>
            </button>
            
            <button
              onClick={handleConnectionStart}
              className="flex items-center space-x-1 px-2 py-1 text-xs text-blue-600 hover:bg-blue-50 rounded"
            >
              <Zap className="w-3 h-3" />
              <span>Connect</span>
            </button>
          </div>
        )}
      </div>

      {/* Connection Line Preview */}
      {isConnecting && (
        <div className="absolute top-1/2 left-full w-8 h-0.5 bg-purple-500 opacity-50 animate-pulse" />
      )}
    </div>
  );
};

const ConnectionLine = ({ connection, nodes }) => {
  const sourceNode = nodes.find(n => n.id === connection.source_node_id);
  const targetNode = nodes.find(n => n.id === connection.target_node_id);

  if (!sourceNode || !targetNode) return null;

  const sourceX = sourceNode.position.x + 200; // Node width
  const sourceY = sourceNode.position.y + 40; // Node height / 2
  const targetX = targetNode.position.x;
  const targetY = targetNode.position.y + 40;

  // Calculate control points for curved line
  const controlX1 = sourceX + (targetX - sourceX) / 3;
  const controlY1 = sourceY;
  const controlX2 = targetX - (targetX - sourceX) / 3;
  const controlY2 = targetY;

  const pathData = `M ${sourceX} ${sourceY} C ${controlX1} ${controlY1}, ${controlX2} ${controlY2}, ${targetX} ${targetY}`;

  return (
    <svg className="absolute inset-0 pointer-events-none z-0" style={{ overflow: 'visible' }}>
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="7"
          refX="9"
          refY="3.5"
          orient="auto"
        >
          <polygon
            points="0 0, 10 3.5, 0 7"
            fill="#6B7280"
          />
        </marker>
      </defs>
      <path
        d={pathData}
        stroke="#6B7280"
        strokeWidth="2"
        fill="none"
        markerEnd="url(#arrowhead)"
        className="drop-shadow-sm"
      />
    </svg>
  );
};

const PipelineCanvas = ({ 
  pipeline, 
  onNodeSelect, 
  onNodeConnect, 
  onNodeDelete, 
  getNodeIcon,
  isMobile 
}) => {
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [canvasOffset, setCanvasOffset] = useState({ x: 0, y: 0 });
  const canvasRef = useRef(null);

  const [{ isOver }, drop] = useDrop({
    accept: 'node',
    drop: (item, monitor) => {
      const offset = monitor.getClientOffset();
      const canvasRect = canvasRef.current?.getBoundingClientRect();
      
      if (offset && canvasRect) {
        const position = {
          x: offset.x - canvasRect.left - canvasOffset.x,
          y: offset.y - canvasRect.top - canvasOffset.y
        };
        return { position };
      }
      return { position: { x: 100, y: 100 } };
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
  });

  const handleNodeSelect = useCallback((node) => {
    setSelectedNodeId(node.id);
    onNodeSelect(node);
  }, [onNodeSelect]);

  const handleCanvasClick = (e) => {
    if (e.target === canvasRef.current) {
      setSelectedNodeId(null);
      onNodeSelect(null);
    }
  };

  return (
    <div
      ref={(node) => {
        canvasRef.current = node;
        drop(node);
      }}
      className={`
        relative w-full h-full overflow-auto bg-gray-50
        ${isOver ? 'bg-blue-50' : ''}
        transition-colors duration-200
      `}
      onClick={handleCanvasClick}
      style={{
        backgroundImage: `
          radial-gradient(circle, #e5e7eb 1px, transparent 1px)
        `,
        backgroundSize: '20px 20px'
      }}
    >
      {/* Empty State */}
      {pipeline.nodes.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
              <Play className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Start Building Your Pipeline
            </h3>
            <p className="text-gray-500 max-w-sm">
              {isMobile 
                ? "Tap components from the palette to add them to your pipeline"
                : "Drag components from the palette to build your data pipeline"
              }
            </p>
          </div>
        </div>
      )}

      {/* Connection Lines */}
      {pipeline.connections.map((connection) => (
        <ConnectionLine
          key={connection.id}
          connection={connection}
          nodes={pipeline.nodes}
        />
      ))}

      {/* Nodes */}
      {pipeline.nodes.map((node) => (
        <PipelineNode
          key={node.id}
          node={node}
          onSelect={handleNodeSelect}
          onDelete={onNodeDelete}
          onConnect={onNodeConnect}
          getNodeIcon={getNodeIcon}
          isSelected={selectedNodeId === node.id}
          isMobile={isMobile}
        />
      ))}

      {/* Drop Indicator */}
      {isOver && (
        <div className="absolute inset-0 border-2 border-dashed border-blue-400 bg-blue-50 bg-opacity-50 pointer-events-none flex items-center justify-center">
          <div className="bg-white px-4 py-2 rounded-lg shadow-lg">
            <p className="text-blue-600 font-medium">Drop component here</p>
          </div>
        </div>
      )}

      {/* Canvas Info */}
      <div className="absolute bottom-4 left-4 bg-white px-3 py-2 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center space-x-4 text-xs text-gray-500">
          <span>{pipeline.nodes.length} nodes</span>
          <span>{pipeline.connections.length} connections</span>
          {!isMobile && <span>Zoom: {Math.round(pipeline.canvas_config.zoom * 100)}%</span>}
        </div>
      </div>
    </div>
  );
};

export default PipelineCanvas;
