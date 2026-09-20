package pe.utec.ventasapi.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Pattern;
import java.time.LocalDate;

/** Actualización parcial: los campos nulos (o ausentes) no se modifican. */
public class PedidoProveedorUpdateRequest {

    private Integer productoId;

    private Integer proveedorId;

    private LocalDate fechaPedido;

    @Min(1)
    private Integer cantidadPedida;

    @Pattern(regexp = "pendiente|en_transito|recibido|cancelado",
            message = "estado debe ser: pendiente, en_transito, recibido o cancelado")
    private String estado;

    private LocalDate fechaEstimadaEntrega;

    public Integer getProductoId() {
        return productoId;
    }

    public void setProductoId(Integer productoId) {
        this.productoId = productoId;
    }

    public Integer getProveedorId() {
        return proveedorId;
    }

    public void setProveedorId(Integer proveedorId) {
        this.proveedorId = proveedorId;
    }

    public LocalDate getFechaPedido() {
        return fechaPedido;
    }

    public void setFechaPedido(LocalDate fechaPedido) {
        this.fechaPedido = fechaPedido;
    }

    public Integer getCantidadPedida() {
        return cantidadPedida;
    }

    public void setCantidadPedida(Integer cantidadPedida) {
        this.cantidadPedida = cantidadPedida;
    }

    public String getEstado() {
        return estado;
    }

    public void setEstado(String estado) {
        this.estado = estado;
    }

    public LocalDate getFechaEstimadaEntrega() {
        return fechaEstimadaEntrega;
    }

    public void setFechaEstimadaEntrega(LocalDate fechaEstimadaEntrega) {
        this.fechaEstimadaEntrega = fechaEstimadaEntrega;
    }
}
