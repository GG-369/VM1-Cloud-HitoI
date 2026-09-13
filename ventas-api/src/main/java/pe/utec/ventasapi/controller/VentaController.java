package pe.utec.ventasapi.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.time.LocalDate;
import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import pe.utec.ventasapi.dto.VentaDiariaRequest;
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
}
