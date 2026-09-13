package pe.utec.ventasapi.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import pe.utec.ventasapi.model.PedidoProveedor;

@Repository
public interface PedidoProveedorRepository extends JpaRepository<PedidoProveedor, Long> {

    List<PedidoProveedor> findByProductoIdOrderByFechaPedidoDesc(Integer productoId);
}
