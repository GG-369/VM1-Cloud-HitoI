package pe.utec.ventasapi.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.persistence.criteria.Predicate;
import jakarta.validation.Valid;
import java.util.ArrayList;
import java.util.List;

import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import pe.utec.ventasapi.dto.PedidoProveedorRequest;
import pe.utec.ventasapi.dto.PedidoProveedorUpdateRequest;
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

    @GetMapping
    @Operation(summary = "Listar pedidos a proveedor (filtros: productoId, proveedorId, estado; paginado)")
    public ResponseEntity<List<PedidoProveedor>> listarPedidos(
            @RequestParam(required = false) Integer productoId,
            @RequestParam(required = false) Integer proveedorId,
            @RequestParam(required = false) String estado,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "50") int size) {
        Specification<PedidoProveedor> filtros = (root, query, cb) -> {
            List<Predicate> predicados = new ArrayList<>();
            if (productoId != null) {
                predicados.add(cb.equal(root.get("productoId"), productoId));
            }
            if (proveedorId != null) {
                predicados.add(cb.equal(root.get("proveedorId"), proveedorId));
            }
            if (estado != null && !estado.isBlank()) {
                predicados.add(cb.equal(root.get("estado"), estado));
            }
            return cb.and(predicados.toArray(new Predicate[0]));
        };
        PageRequest pagina = PageRequest.of(
                Math.max(page, 0), Math.min(Math.max(size, 1), 200),
                Sort.by(Sort.Order.desc("fechaPedido"), Sort.Order.desc("id")));
        return ResponseEntity.ok(pedidoProveedorRepository.findAll(filtros, pagina).getContent());
    }

    // "/{productoId}" ya devuelve el historial por producto, por eso el detalle por id vive en "/detalle/{id}".
    @GetMapping("/detalle/{id}")
    @Operation(summary = "Detalle de un pedido a proveedor por su id")
    public ResponseEntity<PedidoProveedor> obtenerPedido(@PathVariable Long id) {
        return ResponseEntity.ok(buscarPedido(id));
    }

    @PatchMapping("/{id}")
    @Operation(summary = "Actualizar parcialmente un pedido a proveedor")
    public ResponseEntity<PedidoProveedor> actualizarPedido(
            @PathVariable Long id, @Valid @RequestBody PedidoProveedorUpdateRequest request) {
        PedidoProveedor pedido = buscarPedido(id);
        if (request.getProductoId() != null) {
            pedido.setProductoId(request.getProductoId());
        }
        if (request.getProveedorId() != null) {
            pedido.setProveedorId(request.getProveedorId());
        }
        if (request.getFechaPedido() != null) {
            pedido.setFechaPedido(request.getFechaPedido());
        }
        if (request.getCantidadPedida() != null) {
            pedido.setCantidadPedida(request.getCantidadPedida());
        }
        if (request.getEstado() != null) {
            pedido.setEstado(request.getEstado());
        }
        if (request.getFechaEstimadaEntrega() != null) {
            pedido.setFechaEstimadaEntrega(request.getFechaEstimadaEntrega());
        }
        return ResponseEntity.ok(pedidoProveedorRepository.save(pedido));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Eliminar un pedido a proveedor")
    public ResponseEntity<Void> eliminarPedido(@PathVariable Long id) {
        pedidoProveedorRepository.delete(buscarPedido(id));
        return ResponseEntity.noContent().build();
    }

    private PedidoProveedor buscarPedido(Long id) {
        return pedidoProveedorRepository.findById(id).orElseThrow(
                () -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Pedido a proveedor no encontrado"));
    }
}
