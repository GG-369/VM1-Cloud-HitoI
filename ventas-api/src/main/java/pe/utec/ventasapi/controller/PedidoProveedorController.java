package pe.utec.ventasapi.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import pe.utec.ventasapi.dto.PedidoProveedorRequest;
import pe.utec.ventasapi.model.PedidoProveedor;
import pe.utec.ventasapi.repository.PedidoProveedorRepository;

@RestController
@RequestMapping("/api/ventas/pedidos-proveedor")
@Tag(name = "pedidos-proveedor")
public class PedidoProveedorController {

    private final PedidoProveedorRepository pedidoProveedorRepository;

    public PedidoProveedorController(PedidoProveedorRepository pedidoProveedorRepository) {
        this.pedidoProveedorRepository = pedidoProveedorRepository;
    }

    @PostMapping
    @Operation(summary = "Registrar un pedido a proveedor")
    public ResponseEntity<PedidoProveedor> registrarPedido(
            @Valid @RequestBody PedidoProveedorRequest request) {
        PedidoProveedor pedido = new PedidoProveedor();
        pedido.setProductoId(request.getProductoId());
        pedido.setProveedorId(request.getProveedorId());
        pedido.setFechaPedido(request.getFechaPedido());
        pedido.setCantidadPedida(request.getCantidadPedida());
        if (request.getEstado() != null) {
            pedido.setEstado(request.getEstado());
        }
        pedido.setFechaEstimadaEntrega(request.getFechaEstimadaEntrega());
        PedidoProveedor guardado = pedidoProveedorRepository.save(pedido);
        return ResponseEntity.status(HttpStatus.CREATED).body(guardado);
    }

    @GetMapping("/{productoId}")
    @Operation(summary = "Historial de pedidos a proveedor de un producto")
    public ResponseEntity<List<PedidoProveedor>> historialPorProducto(@PathVariable Integer productoId) {
        return ResponseEntity.ok(pedidoProveedorRepository.findByProductoIdOrderByFechaPedidoDesc(productoId));
    }
}
