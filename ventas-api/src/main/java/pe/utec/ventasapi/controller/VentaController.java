package pe.utec.ventasapi.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.persistence.criteria.Predicate;
import jakarta.validation.Valid;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import pe.utec.ventasapi.dto.VentaDiariaRequest;
import pe.utec.ventasapi.dto.VentaDiariaUpdateRequest;
import pe.utec.ventasapi.model.VentaDiaria;
import pe.utec.ventasapi.repository.VentaDiariaRepository;

@RestController
@RequestMapping("/api/ventas")
@Tag(name = "ventas")
public class VentaController {

    private final VentaDiariaRepository ventaDiariaRepository;

    public VentaController(VentaDiariaRepository ventaDiariaRepository) {
        this.ventaDiariaRepository = ventaDiariaRepository;
    }

    @PostMapping
    @Operation(summary = "Registrar una venta diaria")
    public ResponseEntity<VentaDiaria> registrarVenta(@Valid @RequestBody VentaDiariaRequest request) {
        VentaDiaria venta = new VentaDiaria();
        venta.setProductoId(request.getProductoId());
        venta.setFecha(request.getFecha());
        venta.setCantidadVendida(request.getCantidadVendida());
        venta.setPrecioUnitario(request.getPrecioUnitario());
        VentaDiaria guardada = ventaDiariaRepository.save(venta);
        return ResponseEntity.status(HttpStatus.CREATED).body(guardada);
    }

    @GetMapping("/producto/{productoId}")
    @Operation(summary = "Historial de ventas de un producto, opcionalmente acotado a los últimos N días")
    public ResponseEntity<List<VentaDiaria>> historialPorProducto(
            @PathVariable Integer productoId,
            @RequestParam(required = false) Integer dias) {
        List<VentaDiaria> ventas;
        if (dias != null && dias > 0) {
            LocalDate desde = LocalDate.now().minusDays(dias);
            ventas = ventaDiariaRepository.findByProductoIdAndFechaGreaterThanEqualOrderByFechaDesc(
                    productoId, desde);
        } else {
            ventas = ventaDiariaRepository.findByProductoIdOrderByFechaDesc(productoId);
        }
        return ResponseEntity.ok(ventas);
    }

    @GetMapping
    @Operation(summary = "Listar ventas (filtros: productoId, desde, hasta; paginado)")
    public ResponseEntity<List<VentaDiaria>> listarVentas(
            @RequestParam(required = false) Integer productoId,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate desde,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate hasta,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "50") int size) {
        Specification<VentaDiaria> filtros = (root, query, cb) -> {
            List<Predicate> predicados = new ArrayList<>();
            if (productoId != null) {
                predicados.add(cb.equal(root.get("productoId"), productoId));
            }
            if (desde != null) {
                predicados.add(cb.greaterThanOrEqualTo(root.get("fecha"), desde));
            }
            if (hasta != null) {
                predicados.add(cb.lessThanOrEqualTo(root.get("fecha"), hasta));
            }
            return cb.and(predicados.toArray(new Predicate[0]));
        };
        PageRequest pagina = PageRequest.of(
                Math.max(page, 0), Math.min(Math.max(size, 1), 200),
                Sort.by(Sort.Order.desc("fecha"), Sort.Order.desc("id")));
        return ResponseEntity.ok(ventaDiariaRepository.findAll(filtros, pagina).getContent());
    }

    @GetMapping("/{id}")
    @Operation(summary = "Detalle de una venta")
    public ResponseEntity<VentaDiaria> obtenerVenta(@PathVariable Long id) {
        return ResponseEntity.ok(buscarVenta(id));
    }

    @PatchMapping("/{id}")
    @Transactional
    @Operation(summary = "Actualizar parcialmente una venta (recalcula el total)")
    public ResponseEntity<VentaDiaria> actualizarVenta(
            @PathVariable Long id, @Valid @RequestBody VentaDiariaUpdateRequest request) {
        VentaDiaria venta = buscarVenta(id);
        if (request.getProductoId() != null) {
            venta.setProductoId(request.getProductoId());
        }
        if (request.getFecha() != null) {
            venta.setFecha(request.getFecha());
        }
        if (request.getCantidadVendida() != null) {
            venta.setCantidadVendida(request.getCantidadVendida());
        }
        if (request.getPrecioUnitario() != null) {
            venta.setPrecioUnitario(request.getPrecioUnitario());
        }
        return ResponseEntity.ok(ventaDiariaRepository.saveAndFlush(venta));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Eliminar una venta")
    public ResponseEntity<Void> eliminarVenta(@PathVariable Long id) {
        ventaDiariaRepository.delete(buscarVenta(id));
        return ResponseEntity.noContent().build();
    }

    private VentaDiaria buscarVenta(Long id) {
        return ventaDiariaRepository.findById(id).orElseThrow(
                () -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Venta no encontrada"));
    }
}
